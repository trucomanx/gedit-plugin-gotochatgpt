
import json
import os

def default_conf_file(conf_path):
    new_string = """ 
{
    "commands": 
    [
        {
            "name": "rewrite_text",
            "summary": "Rescrever o texto ...",
            "query": "Reescrever o texto corrigindo os problemas de escrita\\n\\n",
            "accelerator":"<Control><Shift>r"
        },
        {
            "name": "traduzir_text",
            "summary": "Traduzir ao ...",
            "query":"Traduzir ao portugues\\n\\n",
            "accelerator":"<Control><Shift>t"
        }
    ],
    "api_key": "PUT-HERE-YOUR-OPENIA-API_KEY"
}
    """
    file = open(conf_path, "w")
    file.write(new_string)
    file.close()

def load_conf_dict(conf_path):
    # Opening JSON file
    dict_conf=None;
    
    if os.path.isfile(conf_path)==False:
        default_conf_file(conf_path);
        
    with open(conf_path) as json_file:
        dict_conf = json.load(json_file);
        
    return dict_conf;
