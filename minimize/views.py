from django.shortcuts import render
from .utils import minimize_grammar, grammar_to_graph, SVG_DIR  # assuming you moved your functions to utils.py
import os
import graphviz

def index(request):
    if request.method == 'POST':
        input_text = request.POST.get('input-text')
        grammar = eval(input_text)
        minimized_grammar = minimize_grammar(grammar)
        dot = grammar_to_graph(minimized_grammar)
        if not os.path.exists(SVG_DIR):
            os.makedirs(SVG_DIR)
        png_filename = 'grammar'
        png_file_path = os.path.join('minimize/static/minimize/svg', png_filename)
        dot.format = 'png'
        dot.render(filename=png_file_path, cleanup=True)
        return render(request, 'minimize/index.html', {'png_filename': png_filename})
    else:
        return render(request, 'minimize/index.html')
