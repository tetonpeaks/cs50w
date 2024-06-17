from random import choice
import traceback

from django.shortcuts import render, redirect

from . import util
from .forms import WikiForm, EditForm
#from .models import Wiki, Edit

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wikipage(request, name):

    print(f"{bcolors.WARNING}request: {bcolors.ENDC}{request}")
    print(f"{bcolors.WARNING}name: {bcolors.ENDC}{name}")

    wikipages = util.list_entries()

    if name in wikipages:
        try:
            return render(request, "encyclopedia/wikipage.html", { "name": name,
                        "markdown": util.md_to_html(util.get_entry(name)) } )
        except Exception as e:
            print(f"{bcolors.WARNING}An exception occurred: {bcolors.ENDC}{str(e)}")
            traceback.print_exc()
    else:
        print(f"{bcolors.FAIL}No wikipage found.{bcolors.ENDC}")
        return render(request, "encyclopedia/error.html", {
            "error": "No such wikipage found."
        })

def search(request):

    name = request.GET['q']

    print(f"{bcolors.WARNING}request: {bcolors.ENDC}{request}")
    print(f"{bcolors.WARNING}name: {bcolors.ENDC}{name}")

    wikipages = util.list_entries()
    similar_pages = [page for page in wikipages if name.lower() in page.lower()]

    if name in wikipages:
        try:
            return redirect("wikipage", name=name)
        except Exception as e:
            print(f"{bcolors.WARNING}An exception occurred: {bcolors.ENDC}{str(e)}")
            traceback.print_exc()
    else:
        msg = "No such wikipage found. Here are similar results:"
        print(f"{bcolors.FAIL}msg: {bcolors.ENDC}{msg}")

        wikipages = util.list_entries()

        return render(request, "encyclopedia/similar.html", {
            "similar_pages": similar_pages,
            "msg": msg,
        })

def newwiki(request):

    print(f"{bcolors.WARNING}request: {bcolors.ENDC}{request}")

    if request.method == "POST":
        wikiform = WikiForm(request.POST)
        if wikiform.is_valid():
            name = wikiform.cleaned_data['name']
            text = wikiform.cleaned_data['text']
            if name.upper() in (entry.upper() for entry in util.list_entries()):
                return render(request, 'encyclopedia/error.html', {
                    "error": f"The wiki for {name} already exists."
                })
            else:
                # Open and write to md file
                formatted_text = f"# {name}\n\n{text}"
                with open(f'entries/{name}.md', 'w') as f:
                    f.write(formatted_text)
            return redirect("wikipage", name=name)
    else:
        form = WikiForm()

    return render(request, "encyclopedia/newwiki.html", {
        'form': form
    })

def editwiki(request, name):

    print(f"{bcolors.WARNING}request: {bcolors.ENDC}{request}")
    print(f"{bcolors.WARNING}request.method: {bcolors.ENDC}{request.method}")
    print(f"{bcolors.WARNING}name: {bcolors.ENDC}{name}")

    #name = request.split('/wiki/')[1]

    if request.method == "POST":

        editform = EditForm(request.POST)

        if editform.is_valid():
            text = editform.cleaned_data['text']
            formatted_text = f"# {name}\n\n{text}"
            with open(f'entries/{name}.md', 'w') as f:
                f.write(formatted_text)
            return redirect('wikipage', name=name)
        # From edit link on wikipage, fill textarea with existing content to edit
        else:
            editform = EditForm({'content': util.get_entry(name)})
    else:
        text = util.get_entry(name)
        lines = text.split('\n')[1:]
        text = '\n'.join(lines)
        lines = text.split('\n')[1:]
        text = '\n'.join(lines)
        editform = EditForm({'text': text})

    return render(request, 'encyclopedia/editwiki.html', { 'editform': editform, 'name': name})

def randomwiki(request):
   name = choice(util.list_entries())
   return redirect("wikipage", name=name)