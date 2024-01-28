'''
    Made by Internetismean, based on the focus tree draw.io parser made by Flaxbeard
'''
import string
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import re
from html import unescape

BASE_EVENT = '''
country_event = {
    id = <namespace>.<number>
    immediate = { log = "[GetDateText]: [Root.GetName]: event <namespace>.<number>" }
    title = <namespace>.<number>.t
    desc = <namespace>.<number>.desc
    is_triggered_only = yes
    picture = x
    <options>
}
'''
BASE_OPTION = '''
    option = { 
        name = <namespace>.<number>.<letter><call>
    }'''

BASE_CALL_OTHER_TAG = '''
        <TAG> = {
            country_event = {
                id = <namespace>.<number>
                days = 1
            }
        }'''

BASE_CALL_SAME_TAG = '''
        country_event = {
            id = <namespace>.<number>
            days = 1
        }'''
# Regex to find options (simple boxes), they don't have a parent and have style rounded=0
OPTION_REGEX = re.compile(r'(<mxCell.*?value((?!style="rounded=1|style="swimlane).)*?>[\s\S]*?</mxCell>)', re.MULTILINE)

# Regex for title boxes
TITLE_REGEX = re.compile(r'(<mxCell.*value((?!style="rounded=0|style="rounded=1).)*?>[\s\S]*?</mxCell>)', re.MULTILINE)

# Regex for description boxes
DESC_REGEX = re.compile(r'(<mxCell.*value((?!parent="1").)*?>[\s\S]*?</mxCell>)', re.MULTILINE)

# Regex to find arrows (have a source and target set to boxes)
ARROW_REGEX = re.compile(r'(<mxCell.*source.*target.*>)')

# Regex to extract various properties of arrows
SOURCE_REGEX = re.compile(r'source="([^"]*)"')
TARGET_REGEX = re.compile(r'target="([^"]*)"')

# Regex to extract various properties of focus boxes
VALUE_REGEX = re.compile(r'value="([^"]*)"')
ID_REGEX = re.compile(r'id="([^"]*)"')
PARENT_REGEX = re.compile(r'parent="([^"]*)"')

TAG_REGEX = re.compile(r'<.*?>')
SPACE_REGEX = re.compile(r'\s+')


def number_check(entry):
    veredict = False
    # Checks a valid number was introduced in the starting number box
    try:
        number = int(entry)
        if number > 0:
            veredict = True
        else:
            messagebox.showerror("Error", "Introduce a valid number")
    except ValueError:
        messagebox.showerror("Error", "Introduce a valid number")
    return veredict


def extract_tag_from_parenthesis(string):  # Done with ChatGPT
    # Find position of starting parenthesis
    initial_index = string.find('(')

    if initial_index != -1:
        # Find position of last parenthesis
        end_index = string.rfind(')')

        if end_index != -1:
            # Extract content from parenthesis
            content = string[initial_index + 1:end_index]

            # Remove parenthesis and content from original string
            resulting_string = string[:initial_index] + string[end_index + 1:]

            return content, resulting_string

    # No parenthesis
    return None, string

def remove_empty_lines(text):
    lines = text.split('\n')
    non_empty_lines = [line.rstrip() for line in lines if line.rstrip() or line.isspace()]
    return '\n'.join(non_empty_lines)

# Represents an event
class Event:
    def __init__(self, event_id, event_namespace, event_number):
        self.id = event_id
        self.namespace = event_namespace
        self.number = event_number
        self.title = ""
        self.desc = ""
        self.options = []

    def __str__(self):
        return str(self.namespace) + "." + str(self.number) + ":" + str(self.id)


class Option:
    def __init__(self, option_id, option_namespace, option_number):
        self.id = option_id
        self.namespace = option_namespace
        self.number = option_number
        self.title = ""
        self.letter = ""
        self.event_id = None
        self.event_tag = None

    def __str__(self):
        return str(self.namespace) + "." + str(self.number) + "." + str(self.letter) + ":" + str(self.id)

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.select_image_file = ''
        self.select_music_file = ''
        self.master = master
        self.pack()
        self.create_widgets()

    # Set up GUI
    def create_widgets(self):
        self.run_script = tk.Button(self)
        self.run_script['text'] = 'Run Program'
        self.run_script['command'] = self.run_app
        self.run_script.pack(side='top', pady=5)

        self.namespace_label = tk.Label(self)
        self.namespace_label['text'] = 'Namespace\n(GER_speer, USA_NPP)'
        self.namespace_label['wraplength'] = 170
        self.namespace_label.pack(side='top', pady=5)
        self.namespace = tk.Entry(self)
        self.namespace.pack(side='top', pady=5)

        self.starting_number_label = tk.Label(self)
        self.starting_number_label['text'] = 'Starting number'
        self.starting_number_label['wraplength'] = 170
        self.starting_number_label.pack(side='top', pady=5)
        self.starting_number = tk.Entry(self)
        self.starting_number.pack(side='top', pady=5)

        self.drawio_data_label = tk.Label(self)
        self.drawio_data_label['text'] = 'Draw.io Data\n(Copied from Extras -> Edit Diagram)'
        self.drawio_data_label.pack(side='top', pady=5)

        self.drawio_data = ScrolledText(self, width=50, height=15, wrap="word")
        self.drawio_data.pack(side='top', pady=5)

    def run_app(self):
        if number_check(self.starting_number.get()):
            namespace = self.namespace.get()
            event_number = int(self.starting_number.get())
            i_contents = self.drawio_data.get(1.0, tk.END).strip()
            events = {}
            options = {}
            # Process all titles
            for e in TITLE_REGEX.findall(i_contents):
                event_id = ID_REGEX.findall(e[0])[0]
                # Extract event title
                text = VALUE_REGEX.findall(e[0])[0]
                text = unescape(text).replace('&nbsp;', ' ')
                text = re.sub(TAG_REGEX, ' ', text)
                text = re.sub(SPACE_REGEX, ' ', text)
                text = text.strip()

                event_title = text

                event = Event(event_id, namespace, event_number)
                event.title = event_title
                events[event_id] = event

                event_number += 1
            # Process event descriptions
            for e in DESC_REGEX.findall(i_contents):
                desc_parent_id = PARENT_REGEX.findall(e[0])[0]
                event = events.get(desc_parent_id)
                text = VALUE_REGEX.findall(e[0])[0]
                text = unescape(text).replace('&nbsp;', ' ')
                text = re.sub(TAG_REGEX, ' ', text)
                text = re.sub(SPACE_REGEX, ' ', text)
                text = text.strip()
                event.desc = text
            # Process event options

            for e in OPTION_REGEX.findall(i_contents):
                option_id = ID_REGEX.findall(e[0])[0]
                # Extract event title
                text = VALUE_REGEX.findall(e[0])[0]
                text = unescape(text).replace('&nbsp;', ' ')
                text = re.sub(TAG_REGEX, ' ', text)
                text = re.sub(SPACE_REGEX, ' ', text)
                text = text.strip()

                tag, option_text = extract_tag_from_parenthesis(text)

                option = Option(option_id, namespace, 0)
                option.title = option_text
                option.event_tag = tag
                options[option_id] = option
            # Process the arrows
            for e in ARROW_REGEX.findall(i_contents):
                source = SOURCE_REGEX.findall(e)[0]
                target = TARGET_REGEX.findall(e)[0]

                source_event = events.get(source)
                target_event = events.get(target)

                # Arrow that goes from event to option - add option to event
                if target_event is None:
                    target_option = options.get(target)
                    source_event.options.append(target_option)
                # Arrow that goes from option to event - add event id to option
                if source_event is None:
                    source_option = options.get(source)
                    source_option.event_id = target_event.id
            # Give numbers and letters to the options
            for event in events.values():
                for i in range(len(event.options)):
                    option = event.options[i]
                    option.letter = string.ascii_lowercase[i]
                    option.number = event.number

            # Output the events
            out = ''
            for event_id in events:
                event = events.get(event_id)
                event_code = BASE_EVENT.replace('<namespace>', event.namespace)
                event_code = event_code.replace('<number>', str(event.number))
                options_code = ''
                for i in range(len(event.options)):
                    option = event.options[i]
                    option_code = BASE_OPTION
                    option_code = option_code.replace('<namespace>', option.namespace)
                    option_code = option_code.replace('<number>', str(option.number))
                    option_code = option_code.replace('<letter>', option.letter)
                    call_code = ''
                    if option.event_tag is not None:
                        option_call_code = BASE_CALL_OTHER_TAG
                        option_call_code = option_call_code.replace('<TAG>', option.event_tag)
                        option_call_code = option_call_code.replace('<namespace>', events.get(option.event_id).namespace)
                        option_call_code = option_call_code.replace('<number>', str(events.get(option.event_id).number))
                        call_code += option_call_code
                    if option.event_tag is None and option.event_id is not None:
                        option_call_code = BASE_CALL_SAME_TAG
                        option_call_code = option_call_code.replace('<namespace>', events.get(option.event_id).namespace)
                        option_call_code = option_call_code.replace('<number>', str(events.get(option.event_id).number))
                        call_code += option_call_code
                    option_code = option_code.replace('<call>', call_code)
                    options_code += option_code
                event_code = event_code.replace('<options>', options_code)
                out += event_code
            # Output focus loc
            out_loc = 'l_english:\n'
            for event in events.values():
                out_loc += event.namespace + "." + str(event.number) + ".t:0 " + '"' + event.title + '"' + "\n"
                out_loc += event.namespace + "." + str(event.number) + ".desc:0 " + '"' + event.desc + '"' + "\n"
                for i in range(len(event.options)):
                    option = event.options[i]
                    out_loc += event.namespace + "." + str(event.number) + "." + option.letter + ":0 " + '"' + option.title + '"' + "\n"
                out_loc += "\n"
            with open('drawio_event_chain.txt', 'w') as o_file:
                o_file.write(out)
            with open('drawio_event_loc.yml', 'w', encoding='utf-8-sig') as o_file:
                o_file.write(out_loc)

root = tk.Tk()
root.geometry('500x510')
root.title('Draw.io Converter')
app = App(master=root)
app.mainloop()
