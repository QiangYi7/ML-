import json
from openai import OpenAI

# 设置OpenAI API密钥
client = OpenAI(api_key='')

def load_data(file_path):
    """加载JSON数据文件。"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading data from {file_path}: {str(e)}")
        return None

def save_data(data, file_path):
    """保存JSON数据到文件。"""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"Error saving data to {file_path}: {str(e)}")

def extract_json_from_text(text):
    """从文本中提取JSON字符串并解析为字典。"""
    try:
        json_str = text.strip()
        # 寻找第一个和最后一个花括号的位置
        start = json_str.find('{')
        end = json_str.rfind('}') + 1
        json_str = json_str[start:end]
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {str(e)}")
        return None

def analyze_episode(episode_name, episode_data, important_items):
    """Call OpenAI API to analyze a single episode."""
    prompt = f"""
    You are a professional story analyst. Please analyze the following episode data and provide detailed analysis for each character.

    **Please note: All output should be in English, including character names and field names.**

    **Please strictly follow these requirements:**

    - **Output only JSON format data, do not add any additional text, explanations, or comments.**
    - **Ensure the output JSON format is correct and can be parsed by a JSON parser.**
    - **Only include items from the provided `important_items` list. Do not add or identify other items.**

    **For each episode, please output according to the following structure:**

    {{
      "{episode_name}": {{
        "whatIf": "{episode_data.get('whatIf', '')}",
        "characters": {{
          "Character Name": {{
            "Interactions_with_Key_Items": {{
              "Item Name": "Description of interaction with the item [Status]"
            }},
            "Actions": "Overall description of character's actions",
            "Relationships": {{
              "Relationship with other character": "Description of relationship"
            }},
            "Emotions": {{
              "Emotion name": "Description of emotion"
            }}
          }},
          ...
        }}
      }}
    }}

    **Here is the episode data:**

    {json.dumps(episode_data['initialRecords'], ensure_ascii=False, indent=2)}

    **Here are the important items:**

    {json.dumps(important_items, ensure_ascii=False, indent=2)}

    **How to generate the Status field:**

    - Based on the events in `initialRecords`, determine the current status of the item. For example:
      - If an item is lost, `[Lost on cliff]`.
      - If an item is hidden, `[Hidden by principal]`.
      - For other necessary statuses, please judge based on the plot and note in the description.

    **Please ensure:**

    - **Output only JSON format data, do not add any additional text.**
    - **All text should be in English.**
    - **JSON format is strictly correct and can be parsed.**
    - **Only include interactions with items from the `important_items` list.**
    - **In `Interactions_with_Key_Items`, the item's status should be included in the description, such as `[Status]`.**
    - **If there are no interactions with important items, keep the field empty.**
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional story analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        # Get response content
        content = response.choices[0].message.content.strip()
        print(f"Response Content for {episode_name}:")
        print(content)

        # Extract JSON from response
        analysis = extract_json_from_text(content)
        if analysis:
            return analysis
        else:
            print(f"Failed to parse JSON for {episode_name}.")
            return None

    except Exception as e:
        print(f"Error analyzing {episode_name}: {str(e)}")
        return None
    
def main():
    # 读取数据文件
    story_data = load_data('/Users/qiangyi/Desktop/rag/发卡.json')
    important_items = load_data('/Users/qiangyi/Desktop/rag/发卡important.json')

    if not story_data or not important_items:
        print("Failed to load necessary data. Exiting.")
        return

    analysis_results = {}

    for storyline, episodes in story_data.items():
        for episode_name, episode_data in episodes.items():
            print(f"Analyzing {episode_name}...")
            analysis = analyze_episode(episode_name, episode_data, important_items['important_items'])
            if analysis:
                analysis_results.update(analysis)
            else:
                print(f"Failed to generate analysis for {episode_name}.")

    # 将所有剧集的分析结果保存到一个文件中
    save_data(analysis_results, '/Users/qiangyi/Desktop/rag/发卡_all_episodes_analysis_third version.json')

    print("Analysis of all episodes has been completed and saved.")
    print("Analysis summary:")
    print(json.dumps(analysis_results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
