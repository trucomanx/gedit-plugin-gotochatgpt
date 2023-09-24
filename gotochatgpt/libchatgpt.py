
import openai 
import sys   
def chatgpt_query(  prompt,
                    api_key,
                    model_engine = "text-davinci-002",
                    max_tokens = 50,
                    temperature = 0.5):
    
    try:
        response = openai.Completion.create(    engine=model_engine, 
                                                prompt=prompt, 
                                                max_tokens=max_tokens, 
                                                n=1, 
                                                stop=None, 
                                                temperature=temperature,
                                                api_key=api_key)
        message = response.choices[0].text.strip();   
        return message;
    except Exception as e:
        return str(e);

