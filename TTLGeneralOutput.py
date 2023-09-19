import pandas as pd
import json

base_url = ''

def is_valid(value):
    return bool(value) and str(value).lower() != 'nan'

def preprocess_life_events(life_events_data):
    mapping = {}
    current_id = 0

    for event_str in life_events_data:
        event_str = str(event_str)  # Convert event_str to string if it isn't already
        # Cleaning up the string and splitting by comma
        events = event_str.replace("[", "").replace("]", "").strip().split(',')
        
        for event in events:
            event = event.strip().replace("'", "")  # Removing quotes and spaces
            
            # If the event is not in the mapping, add it with a new ID
            if event not in mapping:
                mapping[event] = current_id
                current_id += 1
    return mapping


def preprocess_conditions(df):
    """
    Processes the conditions dataframe to create a JSON mapping with conditions_name as the primary key.
    Assigns an incrementing id value for each unique condition, starting from 1.
    """
    json_mapping = {}
    condition_id_counter = 1  # Initialize the counter
    
    # Drop duplicate rows based on the 'conditions_name' column
    df_unique_conditions = df.drop_duplicates(subset='conditions_name')
    
    for _, row in df_unique_conditions.iterrows():
        conditions_name = row["conditions_name"]

        # Skip rows where conditions_name is NaN or None
        if pd.isnull(conditions_name) or conditions_name == "NaN":
            continue

        json_mapping[conditions_name] = {
            "id": condition_id_counter,
            "conditions_num_id": int(row["conditions_num_id"]) if not pd.isnull(row["conditions_num_id"]) else None,
            "conditions_type": row["conditions_type"] if not pd.isnull(row["conditions_type"]) else None
        }
        condition_id_counter += 1  # Increment the counter
    
    return json_mapping

def escape_ttl_string(s):
    """
    Escapes special characters in a string for use in Turtle format.
    """
    return s.replace('"', '\\"')


def append_with_check(triples_list, triple):
    """
    Append the given triple to the triples list.
    Before appending, ensure that the last appended triple (if any) ends with a dot.
    """
    if triples_list and triples_list[-1].endswith(" ."):
        triples_list[-1] = triples_list[-1].replace(" ;", " .")
    
    triples_list.append(triple)

def adjust_punctuation(triples_list):
    """
    Adjusts the punctuation of a list of triples.
    The last triple will end with a '.' while all others will end with ';'
    """
    if triples_list:
        for i in range(len(triples_list) - 1):
            triples_list[i] += ' ;'
        triples_list[-1] += ' .'
    return triples_list

def generate_triples(resource_id, uuid, title, description, provided_language, cost_min, cost_max, output_type, life_events, alternative_titles, df_conditions, df_evidences, df_rules):
    triples = []
    temp_triples = []
    temp_triples.append(f"<{base_url}/id/ps/{resource_id}> a cpsv:PublicService ")
    temp_triples.append(f'  dct:identifier "{uuid}" ')
    temp_triples.append(f'  dct:title "{title}" ')
    if is_valid(alternative_titles):
        temp_triples.append(f'  skos:altLabel """{alternative_titles}""" ')
    if is_valid(description):
        temp_triples.append(f'  dct:description """{description}""" ')
    
    # Check if cost_min and cost_max are not null and add the cv:hasCost triple
    if not pd.isna(cost_min) and not pd.isna(cost_max):
        temp_triples.append(f' cv:hasCost <{base_url}/PublicServices/id/cost/cost_max/cost{resource_id}> ')
        temp_triples.append(f' cv:hasCost <{base_url}/PublicServices/id/cost/cost_min/cost{resource_id}> ')
         
    # Check provided_language and add the corresponding triple(s), if not empty
    if pd.notna(provided_language):
        languages = provided_language.split(',')
        for language in languages:
            language = language.strip()  # Remove any leading/trailing whitespace
            temp_triples.append(f' dct:language "{language}" ;')

    if df_conditions is not None:
        matched_conditions = df_conditions[df_conditions['id'] == resource_id]['conditions_name']
    for condition_name in matched_conditions:
        if condition_name in conditions_mapping:
            condition_id = conditions_mapping[condition_name]["id"]  # Adjusted this line to access the id within the dictionary
            temp_triples.append(f' cv:holdsRequirement<{base_url}/PublicServices/id/requirement/requirement{condition_id}> ')
          
    # Check if life_events is filled, and if so, add the cv:isGroupedBy triple
    condition_found_evidences = resource_id in df_evidences['id'].values
    if condition_found_evidences:
        temp_triples.append(f' cv:hasInput <{base_url}/PublicServices/id/evidence/evidence{resource_id}> ')

    # Check if life_events is filled, and if so, add the cv:isGroupedBy triple
    condition_found_rules = resource_id in df_rules['id'].values
    if condition_found_rules:
        temp_triples.append(f' cv:hasLegalResource <{base_url}/PublicServices/id/rule/rule{resource_id}> ')

    # Add the cv:isGroupedBy triple based on the life_event mapping
    if pd.notna(life_events):
        life_events_list = life_events.replace("[", "").replace("]", "").strip().split(',')
        for life_event in life_events_list:
            life_event = life_event.strip().replace("'", "")
            if life_event in life_events_mapping:
                event_id = life_events_mapping[life_event]
                temp_triples.append(f' cv:isGroupedBy<{base_url}/PublicServices/id/event/event{event_id}> ')

    # Check if output_type is filled, and if so, add the cpsv:produces triple
    if pd.notna(output_type):
        temp_triples.append(f' cpsv:produces <{base_url}/PublicServices/id/praxis/praxis{resource_id}> ')

    temp_triples = adjust_punctuation(temp_triples)
    for triple in temp_triples:
        append_with_check(triples, triple)

    return temp_triples

def append_additional_triples(triples_list, resource_id, cost_min, cost_max, output_type, life_events, df_conditions, df_evidences, df_rules):
    """
    This function appends additional triples based on the conditions for a given resource_id.
    
    Parameters:
    - resource_id: The ID of the resource for which to append the conditions.
    - df_conditions: DataFrame containing the conditions data.
    - conditions_mapping: Dictionary mapping condition names to their IDs from the JSON file.
    - base_url: Base URL for constructing the triples.
    
    Returns:
    - List of triples.
    """
        
    triples = []

    # Add new lines for cost_min and cost_max if available
    if not pd.isna(cost_min):
        triples.append(f" <{base_url}/PublicServices/id/cost/cost_min/cost{resource_id}> a cv:Cost ;")
        triples.append(f"   cv:value {cost_min} ;")
        triples.append('    cv:currency "Euro" ;')
        triples.append('    dct:description "Min Cost" .')
            
    if not pd.isna(cost_max):
        triples.append(f" <{base_url}/PublicServices/id/cost/cost_max/cost{resource_id}> a cv:Cost ;")
        triples.append(f"   cv:value {cost_max} ;")
        triples.append('    cv:currency "Euro" ;')
        triples.append('    dct:description "Max Cost" .')

    if not pd.isna(output_type):
        triples.append(f" <{base_url}/PublicServices/id/praxis/praxis{resource_id}> a cv:Output ;")
        if is_valid(output_type):
            triples.append(f'   dct:title "{output_type}" .')


    # Check if the resource_id is present in the ProcessConditions.csv and append cv:holdsRequirement triple
    matching_evidences = df_evidences[df_evidences['id'] == resource_id]
    for _, row in matching_evidences.iterrows():
        temp_triples = []
        if is_valid(row["evidence_description"]):
            temp_triples.append(f' <{base_url}/PublicServices/id/evidence/evidence{resource_id}> a cv:Evidence ')
            if is_valid(row["evidence_num_id"]):
                temp_triples.append(f'   cv:identifier "{row["evidence_num_id"]}" ')
            if is_valid(row["evidence_description"]):
                temp_triples.append(f'   cv:name """{row["evidence_description"]}""" ')
            if is_valid(row["evidence_type"]):
                temp_triples.append(f'   dct:type "{row["evidence_type"]}" ')
            if is_valid(row["evidence_related_url"]):
                temp_triples.append(f'   cv:relatedDocumentation "{row["evidence_related_url"]}" ')

        temp_triples = adjust_punctuation(temp_triples)
        for triple in temp_triples:
            append_with_check(triples, triple)

    # Check if the resource_id is present in the ProcessConditions.csv and append cv:holdsRequirement triple
    matching_rules = df_rules[df_rules['id'] == resource_id]
    for _, row in matching_rules.iterrows():
        temp_triples = []
        temp_triples.append(f' <{base_url}/PublicServices/id/rule/rule{resource_id}> a eli:LegalResource ')
        if is_valid(row["rule_ada"]):
            temp_triples.append(f'   dct:identifier "{row["rule_ada"]}" ')
        if is_valid(row["rule_description"]):
            temp_triples.append(f'   dct:description "{escape_ttl_string(row["rule_description"])}" ')

        temp_triples = adjust_punctuation(temp_triples)
        for triple in temp_triples:
            append_with_check(triples, triple)

    triples_list.append(triples)

# Read the CSV file using the pipe ('|') delimiter
csv_file_path = 'ProcessGeneral.csv'
df = pd.read_csv(csv_file_path, delimiter='*')

# Load the ProcessConditions.csv data
df_conditions = pd.read_csv("ProcessConditions.csv", delimiter='*')
df_conditions.columns = ['id', 'conditions_name', 'conditions_num_id', 'conditions_type']
df_conditions['id'] = df_conditions['id'].astype(int)

# Load the ProcessEvidences.csv data
df_evidences = pd.read_csv("ProcessEvidence.csv", delimiter='*')
df_evidences.columns = ['id', 'evidence_description', 'evidence_num_id', 'evidence_owner', 'evidence_related_url', 'evidence_type']
df_evidences['id'] = df_evidences['id'].astype(int)

# Load the ProcessEvidences.csv data
df_rules = pd.read_csv("ProcessRules.csv", delimiter='*')
df_rules.columns = ['id', 'rule_ada', 'rule_description']
df_rules['id'] = df_rules['id'].astype(int)

# Preprocess the life_events column and generate the mapping
life_events_mapping = preprocess_life_events(df['life_events'].tolist())
with open('life_events_mapping.json', 'w', encoding='utf-8') as json_file:
    json.dump(life_events_mapping, json_file, ensure_ascii=False, indent=4)

# Preprocess the conditions and generate the mapping
conditions_mapping = preprocess_conditions(df_conditions)
with open('conditions_mapping.json', 'w', encoding='utf-8') as json_file:
    json.dump(conditions_mapping, json_file, ensure_ascii=False, indent=4)

triples_list = [generate_triples(row['id'], row['uuid'], row['official_title'], row['description'], row['provided_language'], row['cost_min'], row['cost_max'], row['output_type'], row['life_events'], row['alternative_titles'], df_conditions, df_evidences, df_rules ) for index, row in df.iterrows()]

# Append additional triples
for index, row in df.iterrows():
    append_additional_triples(triples_list, row['id'], row['cost_min'], row['cost_max'], row['output_type'], row['life_events'], df_conditions, df_evidences, df_rules)

# Append triples for each unique condition from the mapping
added_conditions = set()
triples_conditions = []
for condition_name, condition_data in conditions_mapping.items():
    condition_id = condition_data["id"]
    if condition_id not in added_conditions:
        triples_conditions.append(f' <{base_url}/PublicServices/id/requirement/requirement{condition_id}> a cv:Requirement ;')
        if is_valid(condition_data["conditions_num_id"]):
            triples_conditions.append(f'   cv:identifier "{condition_data["conditions_num_id"]}" ;')
        if is_valid(condition_name):
            triples_conditions.append(f'   dct:title "{condition_name}" ;')
        if is_valid(condition_data["conditions_type"]):
            triples_conditions.append(f'   dct:type "{condition_data["conditions_type"]}" .')
        added_conditions.add(condition_id)

triples_list.append(triples_conditions)

# Append triples for each unique life event from the mapping
triples_lifeEvents = []
for life_event, event_id in life_events_mapping.items():
    triples_lifeEvents.append(f' <{base_url}/PublicServices/id/event/event{event_id}> a cv:LifeEvent ;')
    triples_lifeEvents.append(f'   cv:name "{life_event}" .')
triples_list.append(triples_lifeEvents)

# Flatten the list of lists into a single list
triples = [triple for sublist in triples_list for triple in sublist]

# Write the triples to the TTL file
with open("generated_data.ttl", "w") as f:
    f.write("@prefix schema: <https://schema.org/> .\n")
    f.write("@prefix eli: <http://data.europa.eu/eli/ontology#> .\n")
    f.write("@prefix cv: <http://data.europa.eu/m8g/> .\n")
    f.write("@prefix adms: <http://www.w3.org/ns/adms#> .\n")
    f.write("@prefix dct: <http://purl.org/dc/terms/> .\n")
    f.write("@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n")
    f.write("@prefix dcat: <http://www.w3.org/ns/dcat#> .\n")
    f.write("@prefix locn: <http://www.w3.org/ns/locn#> .\n")
    f.write("@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n")
    f.write("@prefix cpsv: <http://purl.org/vocab/cpsv#> .\n")
    f.write("\n")
    f.write("\n".join(triples))