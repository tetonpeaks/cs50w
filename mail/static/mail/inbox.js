document.addEventListener('DOMContentLoaded', function () {

    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', compose_email);

    document.querySelector('#compose-form').onsubmit = compose_submit;

    // By default, loopoad the inbox
    load_mailbox('inbox');
});

// -----------------------------------------------------------------------------------
function compose_email() {

    // Show compose view and hide other view
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';
    document.querySelector('#email-view').style.display = 'none';


    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
}

function compose_submit() {
    const compose_recipients = document.querySelector('#compose-recipients').value;
    const compose_subject = document.querySelector('#compose-subject').value;
    const compose_body = document.querySelector('#compose-body').value;
    // console.log(compose_recipients, compose_subject, compose_body);

    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
            recipients: compose_recipients,
            subject: compose_subject,
            body: compose_body
        })
    })
    .then(response => response.json())
    .then(result => {
            load_mailbox('inbox');
        });
    return false;
}

function load_mailbox(mailbox) {
    //console.log("mailbox: ", mailbox)
    fetch(`/emails/${mailbox}`)
        .then(response => response.json())
        .then(emails => {
            //console.log(emails)
            //console.log("emails: ", emails)
            for (let i of Object.keys(emails)) {
                const elem_email = document.createElement('div');
                elem_email.classList.add('email');
                if (emails[i].read) {
                    elem_email.classList.add('is_read');
                }
                // console.log(i)
                elem_email.innerHTML = `
                    <div>Subject: ${emails[i].subject}</div>
                    <div>Sender: ${emails[i].sender}</div>
                    <div>Date: ${emails[i].timestamp}</div>
                `;
                // console.log(emails[i].id)
                elem_email.addEventListener('click', () => load_email(emails[i].id, mailbox));

                // console.log(elem_email)
                document.querySelector('#emails-view').append(elem_email);
            };
        });

    // Show emails view and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'none';

    // Show the mailbox name
    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
}

function load_email(id, mailbox) {

    let sent_flag = false;
    //console.log(mailbox)
    if (mailbox==="sent"){
        sent_flag = true;
    }

    // Show email view and hide mailbox
    document.querySelector('#email-view').style.display = 'block';
    document.querySelector('#emails-view').style.display = 'none';

    fetch(`/emails/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
                read: true
        })
    })

    fetch(`/emails/${id}`)
        .then(response => response.json())
        .then(email => {
            if (sent_flag == true) {
                document.querySelector('#email-view').innerHTML = `
                <div>From: ${email.sender}</div>
                <div>To: ${email.recipients}</div>
                <div>Subject: ${email.subject}</div>
                <div>Timestamp: ${email.timestamp}</div>

                <div class="email-buttons">
                    <button class="btn-email" id="reply">Reply</button>
                </div>
                <textarea readonly>${email.body}</textarea>
                `;

            } else {
                document.querySelector('#email-view').innerHTML = `
                <div>From: ${email.sender}</div>
                <div>To: ${email.recipients}</div>
                <div>Subject: ${email.subject}</div>
                <div>Timestamp: ${email.timestamp}</div>

                <div class="email-buttons">
                    <button class="btn-email" id="reply">Reply</button>
                    <button class="btn-email" id="archive">${email["archived"] ? "Unarchive" : "Archive"}</button>
                </div>
                <textarea readonly>${email.body}</textarea>
                `;

                document.querySelector('#archive').addEventListener('click', () => {
                    fetch(`/emails/${id}`, {
                            method: 'PUT',
                            body: JSON.stringify({ archived: !email.archived })
                        })
                        .then(email => {
                            // console.log(email);
                            load_mailbox('inbox');
                        });
                })
            }

        document.querySelector('#reply').addEventListener('click', () => {

            document.querySelector('#emails-view').style.display = 'none';
            document.querySelector('#compose-view').style.display = 'block';
            document.querySelector('#email-view').style.display = 'none';

            if (sent_flag === true) {
                document.querySelector('#compose-recipients').value = email.recipients;
            }
            else {
                document.querySelector('#compose-recipients').value = email.sender;
            }

            //console.log('email.sender: ', email.sender)
            //console.log('email.recipients: ', email.recipients)

            if (email.subject.slice(0,3) != "Re:") {
                document.querySelector('#compose-subject').value = "Re:" + email.subject;
                }
            else {
                document.querySelector('#compose-subject').value = email.subject;
            }

            document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote:\n\n${email.body}\n\n`;
        })
    })
}