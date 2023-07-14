from flask import Flask, render_template, request, send_from_directory
from collections import defaultdict
import graphviz
import os

app = Flask(__name__)

SVG_DIR = 'svg'
def chomsky_normal_form(grammar):
    new_grammar = defaultdict(list)
    non_terminal_counter = 1

    for non_terminal, rules in grammar.items():
        for rule in rules:
            if len(rule) == 1:  # Terminal rules (A -> a)
                new_non_terminal = f"{non_terminal}{non_terminal_counter}"
                non_terminal_counter += 1
                new_grammar[new_non_terminal] = [[rule[0]]]
                new_grammar[non_terminal].append([new_non_terminal])
            elif len(rule) == 2:  # Non-terminal rules (A -> BC)
                new_grammar[non_terminal].append(rule)
            else:  # Rules with more than 2 symbols (A -> BCD)
                prev_non_terminal = rule[0]
                for symbol in rule[1:]:
                    new_non_terminal = f"{non_terminal}{non_terminal_counter}"
                    non_terminal_counter += 1
                    new_grammar[new_non_terminal] = [[symbol]]
                    new_grammar[prev_non_terminal].append([new_non_terminal])
                    prev_non_terminal = new_non_terminal

    return new_grammar

def identify_equivalent(grammar):
    non_terminals = list(grammar.keys())
    n = len(non_terminals)
    equivalent_pairs = set()

    for i in range(n):
        for j in range(i + 1, n):
            Ai, Aj = non_terminals[i], non_terminals[j]
            if all([(rule in grammar[Aj]) for rule in grammar[Ai]]) and all([(rule in grammar[Ai]) for rule in grammar[Aj]]):
                equivalent_pairs.add((Ai, Aj))

    return equivalent_pairs

def merge_equivalent(grammar, equivalent_pairs):
    merged_grammar = defaultdict(list)

    # Create a mapping from old non-terminals to new non-terminals
    mapping = {}
    for non_terminal in grammar.keys():
        if any([non_terminal in pair for pair in equivalent_pairs]):
            for pair in equivalent_pairs:
                if non_terminal in pair:
                    mapping[non_terminal] = min(pair)
                    break
        else:
            mapping[non_terminal] = non_terminal

    # Replace old non-terminals with the new non-terminals in the grammar
    for non_terminal, rules in grammar.items():
        for rule in rules:
            new_rule = [mapping[symbol] if symbol in mapping else symbol for symbol in rule]
            merged_grammar[mapping[non_terminal]].append(new_rule)

    return merged_grammar

def remove_unreachable(grammar):
    reachable = set()
    new_grammar = defaultdict(list)

    def visit(symbol):
        if symbol not in reachable:
            reachable.add(symbol)
            for rule in grammar[symbol]:
                for next_symbol in rule:
                    visit(next_symbol)

    visit('S')

    for non_terminal in reachable:
        new_grammar[non_terminal] = grammar[non_terminal]

    return new_grammar

def remove_unproductive(grammar):
    productive = set()
    changed = True

    while changed:
        changed = False
        for non_terminal, rules in grammar.items():
            if non_terminal not in productive:
                for rule in rules:
                    if all([(symbol in productive) or (symbol == '') for symbol in rule]):
                        productive.add(non_terminal)
                        changed = True
                        break

    new_grammar = {non_terminal: rules for non_terminal, rules in grammar.items() if non_terminal in productive}

    return new_grammar

def original_form(grammar):
    new_grammar = defaultdict(list)

    for non_terminal, rules in grammar.items():
        for rule in rules:
            new_rule = [symbol for symbol in rule if symbol != '']
            if new_rule:
                new_grammar[non_terminal].append(new_rule)

    return new_grammar

def minimize_grammar(grammar):
    chomsky_grammar = chomsky_normal_form(grammar)
    equivalent_pairs = identify_equivalent(chomsky_grammar)
    merged_grammar = merge_equivalent(chomsky_grammar, equivalent_pairs)
    reachable_grammar = remove_unreachable(merged_grammar)
    productive_grammar = remove_unproductive(reachable_grammar)
    minimized_grammar = original_form(productive_grammar)
    return minimized_grammar

def grammar_to_graph(grammar):
    dot = graphviz.Digraph()
    for non_terminal, rules in grammar.items():
        dot.node(non_terminal)
        for rule in rules:
            dot.node(str(rule))
            dot.edge(non_terminal, str(rule))
    return dot

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/', methods=['POST'])
def process_input():
    input_text = request.form['input-text']
    grammar = eval(input_text)
    minimized_grammar = minimize_grammar(grammar)
    dot = grammar_to_graph(minimized_grammar)
    if not os.path.exists(SVG_DIR):
        os.makedirs(SVG_DIR)
    png_filename = 'grammar'
    png_file_path = os.path.join(SVG_DIR, png_filename)
    dot.format = 'png'
    dot.render(filename=png_file_path, cleanup=True)
    print(f"PNG Filename: {png_filename}")  # Add this line
    return render_template('index.html', png_filename=png_filename)

@app.route('/svg/<filename>')
def serve_svg(filename):
    full_file_path = os.path.join(SVG_DIR, filename)
    print(f"Serving file: {full_file_path}")
    return send_from_directory(SVG_DIR, filename)


if __name__ == '__main__':
    app.run(debug=True)