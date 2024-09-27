import json
import re
from openai import OpenAI

client = OpenAI(api_key='')

summary_cache = {}
key_items_cache = {}

def update_summary_and_key_items(previous_summary, previous_key_items, current_scene, episode_number):
    """
    使用GPT模型更新摘要和关键物品状态。

    参数：
        previous_summary (str): 之前的摘要。
        previous_key_items (dict): 之前的关键物品状态字典。
        current_scene (dict): 当前场景。
        episode_number (int): 当前集数。

    返回：
        tuple: (更新后的摘要, 更新后的关键物品状态字典)
    """
    # 使用 initialRecords 中的内容
    current_scene_text = '\n'.join(current_scene['initialRecords'])

    # 将之前的关键物品状态转换为文本
    key_items_text = ""
    for item_name, item_info in previous_key_items.items():
        key_items_text += f"- {item_name}: [Status: {item_info['status']}, Last Known Location/Owner: {item_info['location']}, Current Importance: {item_info['importance']}]\n"

    prompt = f"""
As a careful reader, you need to analyze the development of the story in depth, paying special attention to key items that have a significant impact on the plot and character development. As you read, continue to update and expand your analysis to build a comprehensive picture of the story.

You are currently reading **Episode {episode_number}**.

Based on the previous summary and the current episode, please provide an updated analysis covering the following areas:

**Story Development:**

- Outline the overall plot direction and key events.
- Highlight how new events connect to or develop previous plots.

**Major Turning Points:**

- Describe important plot twists or escalations of conflict.
- Analyze how these turning points affect the overall narrative and character trajectory.

**Character Analysis:**

For each major character and important supporting character:

- Briefly describe their role in the story.
- Examine their psychological state, emotional reactions, and motivations.
- Track their development over time, noting any major changes or revelations.

**Character Relationships:**

- Analyze the interactions and relationship dynamics between characters.
- Note any changes in relationships and their impact on the story.

**Key Item Tracking:**

Identify and track items that have a significant impact on the plot or character development.

For each key item, provide:

- **Item Name**
- **Current Status** (e.g., Owned, Lost, Damaged, Changed)
- **Last Known Location or Owner**
- **Current Importance to the Plot or Character**

Only include items that truly impact the story. Avoid listing insignificant everyday items.

**Unresolved Conflicts:**

- Identify any unresolved conflicts, unresolved storylines, or suspense elements.

**Previous Summary:**

{previous_summary}

**Previous Key Items and Their Statuses:**

{key_items_text}

**Current Episode ({episode_number}):**

{current_scene_text}

Please provide the updated summary and a list of key items with their statuses in the following format:

**Updated Summary:**
[Your updated summary here]

**Updated Key Items and Their Statuses:**

Item Name:
- Current Status: [Status]
- Last Known Location/Owner: [Location/Owner]
- Current Importance: [Importance]

[More items...]

For items that have changed status, please update the corresponding item's status. This is for particularly important items and major mission changes. If not, please do not force it in, as it will only destroy the integrity of the summary.
"""

    # 打印发送给 GPT 的更新提示
    print("\n--- 发送给 GPT 的更新提示 ---\n")
    print(prompt)
    print("\n--- 结束 GPT 的更新提示 ---\n")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a professional story analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        if response and response.choices and response.choices[0].message:
            content = response.choices[0].message.content.strip()

            # 打印 GPT 生成的更新摘要和关键物品
            print("\n--- GPT 生成的更新摘要和关键物品 ---\n")
            print(content)
            print("\n--- 结束 GPT 生成的更新摘要和关键物品 ---\n")

            # 分割更新的摘要和关键物品
            if "**Updated Key Items and Their Statuses:**" in content:
                summary_part, key_items_part = content.split("**Updated Key Items and Their Statuses:**", 1)
                updated_summary = summary_part.replace("**Updated Summary:**", "").strip()
                key_items_text = key_items_part.strip()

                # 解析关键物品及其状态
                updated_key_items = {}
                items = key_items_text.split("\n\n")
                for item in items:
                    lines = item.strip().split('\n')
                    if len(lines) >= 4:
                        item_name_line = lines[0]
                        status_line = lines[1]
                        location_line = lines[2]
                        importance_line = lines[3]

                        item_name = item_name_line.replace("Item Name:", "").strip()
                        status = status_line.replace("- Current Status:", "").strip()
                        location = location_line.replace("- Last Known Location/Owner:", "").strip()
                        importance = importance_line.replace("- Current Importance:", "").strip()

                        updated_key_items[item_name] = {
                            'status': status,
                            'location': location,
                            'importance': importance
                        }
                return updated_summary, updated_key_items
            else:
                # 如果没有明显的分割，则返回整个内容作为摘要，关键物品不变
                updated_summary = content
                updated_key_items = previous_key_items
                return updated_summary, updated_key_items
        else:
            return previous_summary, previous_key_items
    except Exception as e:
        print(f"Error updating summary and key items: {str(e)}")
        return previous_summary, previous_key_items

def evaluate_scene(previous_summary, previous_key_items, current_scene, next_scene, episode_number):
    """
    评估当前场景在叙事进展中的连贯性。

    参数：
        previous_summary (str): 前几场景的摘要。
        previous_key_items (dict): 前几场景的关键物品状态字典。
        current_scene (dict): 当前场景。
        next_scene (dict): 下一场景。
        episode_number (int): 当前集数。

    返回：
        tuple: 包含评分和评估理由的元组。
    """
    # 使用 initialRecords 中的内容
    current_scene_text = '\n'.join(current_scene['initialRecords'])
    next_scene_text = '\n'.join(next_scene['initialRecords']) if next_scene else "without next scene"

    # 将之前的关键物品状态转换为文本
    key_items_text = ""
    for item_name, item_info in previous_key_items.items():
        key_items_text += f"- {item_name}: [Status: {item_info['status']}, Last Known Location/Owner: {item_info['location']}, Current Importance: {item_info['importance']}]\n"

    prompt = f"""
As a literary expert, critically evaluate the coherence of the **Current Episode ({episode_number})** within the context of its narrative progression from the **Previous Summary**. Pay special attention to the continuity and consistency of key items and their statuses.

**Key Items from Previous Episodes:**
{key_items_text}

**Key Aspects to Evaluate:**

1. **Character Consistency** - Evaluate whether the actions and dialogues of main characters in this scene align with their established traits. Note any inconsistencies and assess if they are justified by new developments.

2. **Plot Progression** - Analyze how this scene contributes to the overall story. Assess whether newly introduced elements logically extend the plot and effectively advance or resolve narrative threads.

3. **Emotional and Psychological Realism** - Review the authenticity of the main characters' emotional and psychological responses. Evaluate whether these reactions are believable and consistent with their character development and the situation.

4. **Foreshadowing and Setup for the Next Episode** - Examine how this scene prepares for subsequent developments. Consider whether it hints at future twists or sets the groundwork for upcoming narrative shifts.

5. **Continuity and Consistency in Story Elements** - Examine the episode for any inconsistencies or continuity errors, such as objects appearing or disappearing without explanation, conflicting information, or events that contradict prior established facts. Pay particular attention to items that were lost or destroyed in previous episodes but reappear without explanation. Assess how these issues impact the narrative coherence.

Provide a **balanced and critical** evaluation for each criterion above. Point out both the strengths and weaknesses of the episode, especially regarding the key items. Ensure that your reasoning **clearly supports** the score you assign.

**Previous Summary:**

{previous_summary}

**Current Episode ({episode_number}):**

{current_scene_text}

**Next Episode:**

{next_scene_text}

**Score (0-5) and Justification:**

**Scoring Guidelines:**

- **5 (Excellent):** The episode is exceptionally coherent, with strong character consistency, significant plot progression, authentic emotional responses, and no logical inconsistencies. Key items are used consistently throughout. There are virtually no flaws.

- **4 (Good):** The episode is generally coherent, but there are minor issues in character consistency, plot progression, emotional realism, or minor inconsistencies with key items that slightly detract from the overall narrative.

- **3 (Fair):** The episode has moderate coherence, with noticeable problems, including some inconsistencies with key items that affect the narrative flow.

- **2 (Poor):** The episode has significant coherence issues, with major inconsistencies, including significant continuity errors involving key items.

- **1 (Very Poor):** The episode is highly incoherent, with severe flaws, including critical continuity errors with key items that undermine the narrative.

- **0 (Unacceptable):** The episode is completely incoherent, with fundamental flaws such as key items reappearing or disappearing without any explanation, making the episode nonsensical.
"""

    # 打印发送给 GPT 的评估提示
    print("\n--- 发送给 GPT 的评估提示 ---\n")
    print(prompt)
    print("\n--- 结束 GPT 的评估提示 ---\n")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a meticulous literary critic specializing in narrative coherence."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        if response and response.choices and response.choices[0].message:
            content = response.choices[0].message.content.strip()

            # 打印 GPT 的评估响应
            print("\n--- GPT 的评估响应 ---\n")
            print(content)
            print("\n--- 结束 GPT 的评估响应 ---\n")

            # 使用正则表达式提取评分
            match = re.search(r"Score\s*[:：]\s*(\d+)", content, re.IGNORECASE)
            if match:
                score = int(match.group(1))
            else:
                score = None
            reasoning = content
            return score, reasoning
        else:
            return None, None
    except Exception as e:
        print(f"Error evaluating episode: {str(e)}")
        return None, None

def main():
    try:
        with open('/Users/qiangyi/Desktop/数据处理3/发卡 copy 4.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"Loaded data from file")
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return

    scenes = []
    episode_keys_list = []

    for storyline_key, storyline_value in data.items():
        for episode_key, episode_value in storyline_value.items():
            match = re.match(r'^Episode\s+(\d+)$', episode_key)
            if not match:
                continue
            episode_number = int(match.group(1))
            scene = {
                'episode_key': episode_key,
                'episode_number': episode_number,
                'initialRecords': episode_value.get('initialRecords', [])
            }
            scenes.append(scene)
            episode_keys_list.append((storyline_key, episode_key))

    # 按照集数排序
    scenes.sort(key=lambda x: x['episode_number'])

    print(f"Processed {len(scenes)} episodes from data")

    # 初始化摘要和关键物品状态
    previous_summary = ""
    previous_key_items = {}

    # 迭代每一集，逐步更新摘要和关键物品状态
    for i, scene in enumerate(scenes):
        episode_key = scene['episode_key']
        episode_number = scene['episode_number']
        print(f"Processing {episode_key}")

        next_scene = scenes[i + 1] if i + 1 < len(scenes) else None

        # 首先评估当前场景
        score, reasoning = evaluate_scene(previous_summary, previous_key_items, scene, next_scene, episode_number)
        if score is None:
            print(f"Cannot evaluate {episode_key}.")
            continue

        print(f"{episode_key}, score: {score}")
        print(f"Evaluation reasoning:\n{reasoning}")

        # 然后更新摘要和关键物品状态
        previous_summary, previous_key_items = update_summary_and_key_items(previous_summary, previous_key_items, scene, episode_number)

        # 更新原始数据结构中的评分和评估理由
        for storyline_key, curr_episode_key in episode_keys_list:
            if curr_episode_key == episode_key:
                data[storyline_key][curr_episode_key]['score'] = score
                data[storyline_key][curr_episode_key]['evaluation_reasoning'] = reasoning
                break

    try:
        with open('/Users/qiangyi/Desktop/数据处理3/发卡 copy 4.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        print("评估完成。结果已写入")
    except Exception as e:
        print(f"Error writing results to file: {str(e)}")

if __name__ == "__main__":
    main()
