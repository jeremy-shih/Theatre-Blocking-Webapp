from flask import Flask, jsonify, request
from flask_cors import CORS
import os

# Start the app and setup the static directory for the html, css, and js files.
app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app)

# This is your 'database' of scripts with their blocking info.
# You can store python dictionaries in the format you decided on for your JSON
   # parse the text files in script_data to create these objects - do not send the text
   # files to the client! The server should only send structured data in the sallest format necessary.
scripts = []

### DO NOT modify this route ###
@app.route('/')
def hello_world():
    return 'Theatre Blocking root route'

### DO NOT modify this example route. ###
@app.route('/example')
def example_block():
    example_script = "O Romeo, Romeo, wherefore art thou Romeo? Deny thy father and refuse thy name. Or if thou wilt not, be but sworn my love And I’ll no longer be a Capulet."

    # This example block is inside a list - not in a dictionary with keys, which is what
    # we want when sending a JSON object with multiple pieces of data.
    return jsonify([example_script, 0, 41, 4])


''' Modify the routes below accordingly to
parse the text files and send the correct JSON.'''

## GET route for script and blocking info
@app.route('/script/<int:script_id>')
def script(script_id):
    # initiate dictionary to return
    dict = {}

    # Check which file the script is in
    for filename in os.listdir("/app/script_data/"):
        if os.path.splitext(filename)[-1] != ".txt":
            continue
        # open script file and read in data
        f = open("/app/script_data/" + filename, "r")
        lines = f.readlines()
        lines = [x.strip() for x in lines]
        f.close()
        if lines[0] == str(script_id):
            afile = open("/app/actors.csv", "r")
            actor_file = []
            for line in afile:
                actor_file.append(line.rstrip('\n'))
            afile.close()
            actor_dict = {}
            for i in range(len(actor_file)):
                actor = actor_file[i].split(',')
                actor_dict[actor[1]] = actor[0]

            # add blocking info into a list
            blocking = []
            for i in range(4, len(lines)):
                part_dict = {}
                curr_line = lines[i]
                part_dict["part_number"] = curr_line[0]
                curr_line = lines[i][3:]
                curr_line_list = curr_line.split(',')
                for j in range(len(curr_line_list)):
                    curr_line_list[j] = curr_line_list[j].lstrip(' ')
                part_dict["char_start"] = curr_line_list[0]
                part_dict["char_end"] = curr_line_list[1]
                actor_pos_list = curr_line_list[2:]
                actor_pos_dict = {}
                actors_positions = []
                actors =[]
                for k in range(len(actor_pos_list)):
                    actor_pos_list[k] = actor_pos_list[k].split('-')
                    actors.append(actor_pos_list[k][0])
                    actors_positions.append(actor_pos_list[k][1])
                    actor_pos_dict[actor_dict[actor_pos_list[k][0]]] = actor_pos_list[k][1]
                part_dict["actors_to_position"] = actor_pos_dict
                part_dict["actors"] = actors
                part_dict["actors_positions"] = actors_positions
                blocking.append(part_dict)

            # Added to dictionary
            line = lines[2]
            dict["script_text"] = line
            dict["actor_number"] = actor_dict
            dict["blocking"] = blocking

    # right now, just sends the script id in the URL
    return jsonify(dict)

## POST route for replacing script blocking on server
# Note: For the purposes of this assignment, we are using POST to replace an entire script.
# Other systems might use different http verbs like PUT or PATCH to replace only part
# of the script.


@app.route('/script', methods=['POST'])
def addBlocking():
    # right now, just sends the original request json
    data = request.json
    script_id = data["scriptNum"]


    # Check which file the script is in
    for filename in os.listdir("/app/script_data/"):
        if os.path.splitext(filename)[-1] != ".txt":
            continue
        # open script file and read in data
        f = open("/app/script_data/" + filename, "r")
        lines = f.readlines()
        lines = [x.strip() for x in lines]
        f.close()

        if lines[0] == str(script_id):
            # Write to script num and line to file
            f = open("/app/script_data/" + filename, "w")
            f.write(script_id + "\n\n")

            # # Write line to file
            block = data["blockDetails"]

            line = ""
            if len(data["blockDetails"]) == 1:
                for i in range(len(data["blockDetails"])):
                    line += (data["blockDetails"][i]["text"]).strip("\"")
                    f.write(line + "\n\n")
            else:
                for i in range(len(data["blockDetails"]) - 1):
                    line += (data["blockDetails"][i]["text"]).strip("\"")
                    f.write(line + "\n\n")

            start_char = 0
            end_char = 0
            for j in range(len(block)):
                whole_part = ""
                whole_part += str(block[j]["part"]) + ". "
                # start_char += end_char
                whole_part = whole_part + str(start_char) + ", "
                end_char += len(block[j]["text"].strip("\"")) - 1
                whole_part = whole_part + str(end_char) + ", "
                name_to_pos = block[j]["actors"]
                for k in range(len(name_to_pos)):
                    whole_part = whole_part + name_to_pos[k][0].strip("\"") + "-" + name_to_pos[k][1].strip("\"")
                    if k < len(name_to_pos) - 1:
                        whole_part = whole_part + ", "
                f.write(whole_part + '\n')

            f.close()

            return jsonify(request.json)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=os.environ.get('PORT', 80))
