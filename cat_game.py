import PySimpleGUI as sg
import os
import sys
from PIL import Image
import io

# --- 增加一个辅助函数来处理资源路径 ---
def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境和PyInstaller打包环境 """
    try:
        # PyInstaller 创建的临时文件夹的路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- 游戏配置与资源 ---
sg.theme('Reddit')
TARGET_IMAGE_SIZE = (400, 400)

# --- 使用 resource_path 函数来定义图片路径 ---
IMAGE_PATHS = {
    'neutral': resource_path('assets/cat_neutral.png'),
    'happy':   resource_path('assets/cat_happy.png'),
    'annoyed': resource_path('assets/cat_annoyed.png')
}

def show_gentle_error(message):
    sg.popup(message, title='呜...出错了喵', custom_text='好的喵')

# 检查图片文件是否存在
for mood, path in IMAGE_PATHS.items():
    if not os.path.exists(path):
        show_gentle_error(f'可恶！图片文件找不到了喵 (路径: {path})\n\n请确保脚本可以找到 "assets" 文件夹。')
        exit()

# --- 核心游戏函数 ---
def play_game(cat_name):
    """封装了完整游戏逻辑的函数，返回用户选择的下一步操作"""

    game_state = {
        'affection': 50, 'stage': 'start', 'cat_mood': 'neutral',
        'cat_name': cat_name, 'approach_attempts': 0
    }

    story_data = {
        'start': {'text': f'一只叫【{cat_name}】的猫咪出现在你家门口，警惕地看着你。', 'mood': 'neutral',
                  'cat_thought': '（这个两脚兽是谁？看起来不太聪明的样子...）', 'choices': {
                'A': {'text': 'A. 慢慢靠近，伸出手', 'effect': {'affection': -5, 'next_stage': 'approach_gently'}},
                'B': {'text': 'B. 拿出食物引诱它', 'effect': {'affection': 10, 'next_stage': 'offer_food'}},
                'C': {'text': 'C. 热情地冲上去抱住', 'effect': {'affection': -20, 'next_stage': 'rush_hug'}}}},
        'approach_gently': {'text': f'【{cat_name}】闻了闻你的手，但还是后退了半步。看起来不是很信任你。', 'mood': 'neutral',
                            'cat_thought': '（离我远点...你身上没有小鱼干的味道。）', 'choices': {
                'A': {'text': 'A. 再试一次', 'effect': {'affection': -10, 'next_stage': 'approach_gently'}},
                'B': {'text': 'B. 拿出食物', 'effect': {'affection': 10, 'next_stage': 'offer_food'}},
                'C': {'text': 'C. 放弃，转身离开', 'effect': {'affection': 0, 'next_stage': 'ending_neutral'}}}},
        'offer_food': {'text': f'食物的香气让【{cat_name}】放下了戒备，它走过来小口地吃了起来。', 'mood': 'happy',
                       'cat_thought': '（嗯...真香！暂时原谅这个人类好了。）', 'choices': {
                'A': {'text': 'A. 趁机摸它的头', 'effect': {'affection': 15, 'next_stage': 'pet_while_eating'}},
                'B': {'text': 'B. 在旁边安静地看着', 'effect': {'affection': 5, 'next_stage': 'watch_quietly'}},
                'C': {'text': 'C. 把食物拿走逗它', 'effect': {'affection': -30, 'next_stage': 'tease_with_food'}}}},
        'rush_hug': {'text': f'“嘶！！”【{cat_name}】被你吓了一跳，对你彻底失望了。它亮出爪子抓了你一下，飞快地逃走了，再也没有出现过。', 'mood': 'annoyed',
                     'cat_thought': '（有坏人啊！！！）', 'choices': {'A': {'text': '', 'effect': {}},
                                                             'B': {'text': '重新开始', 'effect': {'next_stage': 'restart'}},
                                                             'C': {'text': '退出游戏', 'effect': {'next_stage': 'quit'}}}},
        'tease_with_food': {'text': f'你戏弄【{cat_name}】的行为让它非常不满，它弓起背，亮出爪子抓了你一下，飞快地逃走了，再也没有出现过。', 'mood': 'annoyed',
                            'cat_thought': '（？竟敢戏弄本喵！不可饶恕！）', 'choices': {'A': {'text': '', 'effect': {}},
                                                                         'B': {'text': '重新开始',
                                                                               'effect': {'next_stage': 'restart'}},
                                                                         'C': {'text': '退出游戏',
                                                                               'effect': {'next_stage': 'quit'}}}},
        'pet_while_eating': {'text': '它一边吃，一边发出咕噜咕噜的声音，似乎很享受你的抚摸。好感度大幅提升了！', 'mood': 'happy',
                             'cat_thought': '（咕噜咕噜...就是这里...对...再用点力喵...）', 'choices': {
                'A': {'text': 'A. 拿出逗猫棒', 'effect': {'affection': 20, 'next_stage': 'ending_good'}},
                'B': {'text': 'B. 挠它的下巴', 'effect': {'affection': 25, 'next_stage': 'ending_good'}},
                'C': {'text': 'C. (特殊) 你到底喜欢我吗？', 'effect': {'affection': 0, 'next_stage': 'cult_intro'}}}},
        'cult_intro': {'text': f'【{cat_name}】停下进食，抬头看着你：“呵，人类！臣服在喵喵教的圣坛之下罢喵！”', 'mood': 'happy',
                       'cat_thought': '（终于等到这一天了！）',
                       'choices': {'A': {'text': '好的教主！', 'effect': {'affection': 10, 'next_stage': 'cult_question'}},
                                   'B': {'text': '一定教主！', 'effect': {'affection': 10, 'next_stage': 'cult_question'}},
                                   'C': {'text': '谢谢教主！', 'effect': {'affection': 10, 'next_stage': 'cult_question'}}}},
        'cult_question': {'text': '那我们应该怎么做呢喵？', 'mood': 'neutral', 'cat_thought': '（考验你忠诚度的时候到了。）',
                          'choices': {'A': {'text': '摸摸猫猫！', 'effect': {'affection': -5, 'next_stage': 'cult_petting'}},
                                      'B': {'text': '亲亲猫猫！',
                                            'effect': {'affection': -10, 'next_stage': 'cult_petting'}},
                                      'C': {'text': '把所有的财产都献给猫猫！',
                                            'effect': {'affection': 30, 'next_stage': 'cult_petting'}}}},
        'cult_petting': {'text': '很好，人类！我现在允许你摸一下我美丽的皮毛。', 'mood': 'happy', 'cat_thought': '（就一下，不能再多了。）', 'choices': {
            'A': {'text': '摸一下', 'effect': {'affection': 15, 'next_stage': 'ending_cult_good'}},
            'B': {'text': '摸两下', 'effect': {'affection': -10, 'next_stage': 'ending_cult_bad'}},
            'C': {'text': '我要把你摸秃！！！', 'effect': {'affection': -50, 'next_stage': 'ending_cult_bad'}}}},
        'watch_quietly': {'text': f'【{cat_name}】吃完后，舔了舔爪子，抬头看了你一眼，似乎在期待什么。', 'mood': 'neutral',
                          'cat_thought': '（吃饱了...有点无聊...该干点什么呢...）', 'choices': {
                'A': {'text': 'A. 拿出毛线球', 'effect': {'affection': 15, 'next_stage': 'ending_good'}},
                'B': {'text': 'B. 拿出逗猫棒', 'effect': {'affection': 20, 'next_stage': 'ending_good'}},
                'C': {'text': 'C. 和它大眼瞪小眼', 'effect': {'affection': -5, 'next_stage': 'ending_neutral'}}}},
        'ending_good': {'text': f'恭喜！【{cat_name}】完全接纳了你，它蹭着你的腿，从此赖在你家不走了。你成功收获了一只猫！', 'mood': 'happy',
                        'cat_thought': '（哼，这个铲屎官还算合格。）', 'choices': {'A': {'text': '', 'effect': {}},
                                                                     'B': {'text': '重新开始',
                                                                           'effect': {'next_stage': 'restart'}},
                                                                     'C': {'text': '退出游戏',
                                                                           'effect': {'next_stage': 'quit'}}}},
        'ending_neutral': {'text': f'【{cat_name}】深深地看了你一眼，转身消失在了街角。也许明天，它还会出现吧？', 'mood': 'neutral',
                           'cat_thought': '（奇怪的人类...明天再来看看好了。）', 'choices': {'A': {'text': '', 'effect': {}},
                                                                             'B': {'text': '重新开始',
                                                                                   'effect': {'next_stage': 'restart'}},
                                                                             'C': {'text': '退出游戏',
                                                                                   'effect': {'next_stage': 'quit'}}}},
        'ending_bad': {'text': f'【{cat_name}】对你彻底失望了，它亮出爪子抓了你一下，飞快地逃走了，再也没有出现过。', 'mood': 'annoyed',
                       'cat_thought': '（再也别让本喵看到你！）', 'choices': {'A': {'text': '', 'effect': {}}, 'B': {'text': '重新开始',
                                                                                                         'effect': {
                                                                                                             'next_stage': 'restart'}},
                                                                  'C': {'text': '退出游戏',
                                                                        'effect': {'next_stage': 'quit'}}}},
        'ending_cult_good': {'text': f'purrrrrrrrr~ 好舒服喵~ 你成为了教主【{cat_name}】最信赖的铲屎官！', 'mood': 'happy',
                             'cat_thought': '（嗯...可以考虑封你为大祭司...）', 'choices': {'A': {'text': '', 'effect': {}},
                                                                               'B': {'text': '重新开始', 'effect': {
                                                                                   'next_stage': 'restart'}},
                                                                               'C': {'text': '退出游戏', 'effect': {
                                                                                   'next_stage': 'quit'}}}},
        'ending_cult_bad': {'text': f'“啊呜————” 你激怒了教主【{cat_name}】！它在你手上留下了圣痕，并宣布将你逐出喵喵教。', 'mood': 'annoyed',
                            'cat_thought': '（无知的人类，竟敢亵渎神体！）', 'choices': {'A': {'text': '', 'effect': {}},
                                                                          'B': {'text': '重新开始',
                                                                                'effect': {'next_stage': 'restart'}},
                                                                          'C': {'text': '退出游戏',
                                                                                'effect': {'next_stage': 'quit'}}}},
        'ending_annoyed_by_pestering': {'text': f'你反复的试探让【{cat_name}】失去了所有耐心，它不耐烦地“喵！”了一声，转身消失在了黑暗中。',
                                        'mood': 'annoyed', 'cat_thought': '（哼！烦死了！）',
                                        'choices': {'A': {'text': '', 'effect': {}},
                                                    'B': {'text': '重新开始', 'effect': {'next_stage': 'restart'}},
                                                    'C': {'text': '退出游戏', 'effect': {'next_stage': 'quit'}}}}
    }

    image_data = {}
    for mood, path in IMAGE_PATHS.items():
        try:
            img = Image.open(path)
            img.thumbnail(TARGET_IMAGE_SIZE)
            bio = io.BytesIO()
            img.save(bio, format="PNG")
            image_data[mood] = bio.getvalue()
        except Exception as e:
            sg.popup_error(f"处理图片 {path} 时出错: {e}")  # 用 error popup 强制终止
            return 'quit'

    layout = [
        [sg.Image(data=image_data['neutral'], key='--CAT_IMAGE--')],
        [sg.Text('', key='--CAT_THOUGHT--', font=('Helvetica', 11, 'italic'), text_color='grey', size=(50, 2),
                 justification='c')],
        [sg.ProgressBar(100, orientation='h', size=(30, 20), key='--AFFECTION_BAR--',
                        bar_color=('MediumPurple', 'lightgrey'))],
        [sg.Text('好感度', font=('Helvetica', 10), key='--AFFECTION_TEXT--')],
        [sg.Text(size=(50, 3), key='--STORY_TEXT--', font=('Helvetica', 12))],
        [sg.Button('', key='A', size=(20, 2)), sg.Button('', key='B', size=(20, 2)),
         sg.Button('', key='C', size=(20, 2))]
    ]
    window = sg.Window(f'与【{cat_name}】的奇遇', layout, element_justification='c', finalize=True)

    def update_ui(state):
        stage_info = story_data[state['stage']]
        if state['affection'] < 0: state['affection'] = 0
        if state['affection'] > 100: state['affection'] = 100
        window['--AFFECTION_BAR--'].update(state['affection'])
        window['--AFFECTION_TEXT--'].update(f"好感度: {state['affection']}")

        if state['affection'] >= 80:
            state['cat_mood'] = 'happy'
        elif state['affection'] <= 20:
            state['cat_mood'] = 'annoyed'
        else:
            state['cat_mood'] = 'neutral'
        final_mood = stage_info.get('mood', state['cat_mood'])
        window['--CAT_IMAGE--'].update(data=image_data[final_mood])

        window['--STORY_TEXT--'].update(stage_info['text'])
        window['--CAT_THOUGHT--'].update(stage_info.get('cat_thought', ''))

        choices = stage_info.get('choices', {})
        for key in ['A', 'B', 'C']:
            if key in choices and choices[key].get('text'):
                window[key].update(choices[key]['text'], visible=True)
            else:
                window[key].update(visible=False)

    update_ui(game_state)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            window.close()
            return 'quit'

        current_stage_info = story_data[game_state['stage']]
        if 'choices' not in current_stage_info or event not in current_stage_info['choices']:
            continue

        if game_state['stage'] == 'approach_gently' and event == 'A':
            game_state['approach_attempts'] += 1
            if game_state['approach_attempts'] >= 2:
                game_state['stage'] = 'ending_annoyed_by_pestering'
                game_state['affection'] -= 15
                update_ui(game_state)
                continue

        choice_effect = current_stage_info['choices'][event]['effect']
        next_stage = choice_effect.get('next_stage')

        if next_stage == 'quit':
            window.close()
            return 'quit'
        if next_stage == 'restart':
            window.close()
            return 'restart'

        if next_stage:
            game_state['affection'] += choice_effect.get('affection', 0)
            game_state['stage'] = next_stage

        update_ui(game_state)


# --- 主程序入口 ---
def main():
    """主程序，控制游戏的启动和循环"""
    cat_name = sg.popup_get_text('你遇到了一只小猫，给它起个名字吧！', '起名环节')
    if cat_name is None:  # 如果用户点了Cancel或者关闭窗口
        return
    cat_name = cat_name if cat_name else "咪咪"

    # 用一个循环来控制是否重新开始游戏
    while True:
        action = play_game(cat_name)
        if action == 'quit':
            break


if __name__ == "__main__":
    main()



# --- 备份上一版本 ---
"""
import PySimpleGUI as sg
import os
from PIL import Image
import io

# --- 游戏配置与资源 ---
sg.theme('Reddit')

TARGET_IMAGE_SIZE = (400, 400)

IMAGE_PATHS = {
    'neutral': 'assets/cat_neutral.png',
    'happy': 'assets/cat_happy.png',
    'annoyed': 'assets/cat_annoyed.png'
}


def show_gentle_error(message):
    sg.popup(message, title='呜...出错了喵', custom_text='好的喵')


image_data = {}
for mood, path in IMAGE_PATHS.items():
    if not os.path.exists(path):
        show_gentle_error(f'可恶！图片文件找不到了喵 (路径: {path})')
        exit()
    try:
        img = Image.open(path)
        img.thumbnail(TARGET_IMAGE_SIZE)
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        image_data[mood] = bio.getvalue()
    except Exception as e:
        show_gentle_error(f"处理图片 {path} 时出错: {e}")
        exit()

# --- 游戏逻辑部分 ---
cat_name_input = sg.popup_get_text('你遇到了一只小猫，给它起个名字吧！', '起名环节')
cat_name = cat_name_input if cat_name_input else "咪咪"

# 改动：为 game_state 增加一个计数器
game_state = {
    'affection': 50, 'stage': 'start', 'cat_mood': 'neutral',
    'cat_name': cat_name, 'approach_attempts': 0
}

# 改动：为 story_data 增加'cat_thought'内心戏字段和一个新结局
story_data = {
    'start': {
        'text': f'一只叫【{cat_name}】的猫咪出现在你家门口，警惕地看着你。',
        'mood': 'neutral',
        'cat_thought': '（这个两脚兽是谁？看起来不太聪明的样子...）',
        'choices': {
            'A': {'text': 'A. 慢慢靠近，伸出手', 'effect': {'affection': -5, 'next_stage': 'approach_gently'}},
            'B': {'text': 'B. 拿出食物引诱它', 'effect': {'affection': 10, 'next_stage': 'offer_food'}},
            'C': {'text': 'C. 热情地冲上去抱住', 'effect': {'affection': -20, 'next_stage': 'rush_hug'}}
        }
    },
    'approach_gently': {
        'text': f'【{cat_name}】闻了闻你的手，但还是后退了半步。看起来不是很信任你。',
        'mood': 'neutral',
        'cat_thought': '（离我远点...你身上没有小鱼干的味道。）',
        'choices': {
            'A': {'text': 'A. 再试一次', 'effect': {'affection': -10, 'next_stage': 'approach_gently'}},
            'B': {'text': 'B. 拿出食物', 'effect': {'affection': 10, 'next_stage': 'offer_food'}},
            'C': {'text': 'C. 放弃，转身离开', 'effect': {'affection': 0, 'next_stage': 'ending_neutral'}}
        }
    },
    'offer_food': {
        'text': f'食物的香气让【{cat_name}】放下了戒备，它走过来小口地吃了起来。',
        'mood': 'happy',
        'cat_thought': '（嗯...真香！暂时原谅这个人类好了。）',
        'choices': {
            'A': {'text': 'A. 趁机摸它的头', 'effect': {'affection': 15, 'next_stage': 'pet_while_eating'}},
            'B': {'text': 'B. 在旁边安静地看着', 'effect': {'affection': 5, 'next_stage': 'watch_quietly'}},
            'C': {'text': 'C. 把食物拿走逗它', 'effect': {'affection': -30, 'next_stage': 'tease_with_food'}}
        }
    },
    'pet_while_eating': {
        'text': '它一边吃，一边发出咕噜咕噜的声音，似乎很享受你的抚摸。好感度大幅提升了！',
        'mood': 'happy',
        'cat_thought': '（咕噜咕噜...就是这里...对...再用点力喵...）',
        'choices': {
            'A': {'text': 'A. 拿出逗猫棒', 'effect': {'affection': 20, 'next_stage': 'ending_good'}},
            'B': {'text': 'B. 挠它的下巴', 'effect': {'affection': 25, 'next_stage': 'ending_good'}},
            'C': {'text': 'C. (特殊) 你到底喜欢我吗？', 'effect': {'affection': 0, 'next_stage': 'cult_intro'}}
        }
    },
    # ... 其他剧情分支保持不变，此处省略 ...
    'rush_hug': {'text': f'“嘶！！”【{cat_name}】被你吓了一跳，对你彻底失望了。它亮出爪子抓了你一下，飞快地逃走了，再也没有出现过。', 'mood': 'annoyed',
                 'cat_thought': '（有坏人啊！！！）', 'choices': {'A': {'text': '', 'effect': {}},
                                                         'B': {'text': '重新开始', 'effect': {'next_stage': 'restart'}},
                                                         'C': {'text': '退出游戏', 'effect': {'next_stage': 'quit'}}}},
    'tease_with_food': {'text': f'你戏弄【{cat_name}】的行为让它非常不满，它弓起背，亮出爪子抓了你一下，飞快地逃走了，再也没有出现过。', 'mood': 'annoyed',
                        'cat_thought': '（竟敢戏弄本喵！不可饶恕！）', 'choices': {'A': {'text': '', 'effect': {}},
                                                                     'B': {'text': '重新开始',
                                                                           'effect': {'next_stage': 'restart'}},
                                                                     'C': {'text': '退出游戏',
                                                                           'effect': {'next_stage': 'quit'}}}},
    'cult_intro': {'text': f'【{cat_name}】停下进食，抬头看着你：“呵，人类！臣服在喵喵教的圣坛之下罢喵！”', 'mood': 'happy',
                   'cat_thought': '（终于等到这一天了！）',
                   'choices': {'A': {'text': '好的教主！', 'effect': {'affection': 10, 'next_stage': 'cult_question'}},
                               'B': {'text': '一定教主！', 'effect': {'affection': 10, 'next_stage': 'cult_question'}},
                               'C': {'text': '谢谢教主！', 'effect': {'affection': 10, 'next_stage': 'cult_question'}}}},
    'cult_question': {'text': '那我们应该怎么做呢喵？', 'mood': 'neutral', 'cat_thought': '（考验你忠诚度的时候到了。）',
                      'choices': {'A': {'text': '摸摸猫猫！', 'effect': {'affection': -5, 'next_stage': 'cult_petting'}},
                                  'B': {'text': '亲亲猫猫！', 'effect': {'affection': -10, 'next_stage': 'cult_petting'}},
                                  'C': {'text': '把所有的财产都献给猫猫！',
                                        'effect': {'affection': 30, 'next_stage': 'cult_petting'}}}},
    'cult_petting': {'text': '很好，人类！我现在允许你摸一下我美丽的皮毛。', 'mood': 'happy', 'cat_thought': '（就一下，不能再多了。）',
                     'choices': {'A': {'text': '摸一下', 'effect': {'affection': 15, 'next_stage': 'ending_cult_good'}},
                                 'B': {'text': '摸两下', 'effect': {'affection': -10, 'next_stage': 'ending_cult_bad'}},
                                 'C': {'text': '我要把你摸秃！！！',
                                       'effect': {'affection': -50, 'next_stage': 'ending_cult_bad'}}}},
    'watch_quietly': {'text': f'【{cat_name}】吃完后，舔了舔爪子，抬头看了你一眼，似乎在期待什么。', 'mood': 'neutral',
                      'cat_thought': '（吃饱了...有点无聊...该干点什么呢...）',
                      'choices': {'A': {'text': 'A. 拿出毛线球', 'effect': {'affection': 15, 'next_stage': 'ending_good'}},
                                  'B': {'text': 'B. 拿出逗猫棒', 'effect': {'affection': 20, 'next_stage': 'ending_good'}},
                                  'C': {'text': 'C. 和它大眼瞪小眼',
                                        'effect': {'affection': -5, 'next_stage': 'ending_neutral'}}}},
    'ending_good': {'text': f'恭喜！【{cat_name}】完全接纳了你，它蹭着你的腿，从此赖在你家不走了。你成功收获了一只猫！', 'mood': 'happy',
                    'cat_thought': '（哼，这个铲屎官还算合格。）', 'choices': {'A': {'text': '', 'effect': {}}, 'B': {'text': '重新开始',
                                                                                                        'effect': {
                                                                                                            'next_stage': 'restart'}},
                                                                 'C': {'text': '退出游戏',
                                                                       'effect': {'next_stage': 'quit'}}}},
    'ending_neutral': {'text': f'【{cat_name}】深深地看了你一眼，转身消失在了街角。也许明天，它还会出现吧？', 'mood': 'neutral',
                       'cat_thought': '（奇怪的人类...明天再来看看好了。）', 'choices': {'A': {'text': '', 'effect': {}},
                                                                         'B': {'text': '重新开始',
                                                                               'effect': {'next_stage': 'restart'}},
                                                                         'C': {'text': '退出游戏',
                                                                               'effect': {'next_stage': 'quit'}}}},
    'ending_bad': {'text': f'【{cat_name}】对你彻底失望了，它亮出爪子抓了你一下，飞快地逃走了，再也没有出现过。', 'mood': 'annoyed',
                   'cat_thought': '（再也别让本喵看到你！）', 'choices': {'A': {'text': '', 'effect': {}}, 'B': {'text': '重新开始',
                                                                                                     'effect': {
                                                                                                         'next_stage': 'restart'}},
                                                              'C': {'text': '退出游戏', 'effect': {'next_stage': 'quit'}}}},
    'ending_cult_good': {'text': f'purrrrrrrrr~ 好舒服喵~ 你成为了教主【{cat_name}】最信赖的铲屎官！', 'mood': 'happy',
                         'cat_thought': '（嗯...可以考虑封你为大祭司...）', 'choices': {'A': {'text': '', 'effect': {}},
                                                                           'B': {'text': '重新开始',
                                                                                 'effect': {'next_stage': 'restart'}},
                                                                           'C': {'text': '退出游戏',
                                                                                 'effect': {'next_stage': 'quit'}}}},
    'ending_cult_bad': {'text': f'“啊呜————” 你激怒了教主【{cat_name}】！它在你手上留下了圣痕，并宣布将你逐出喵喵教。', 'mood': 'annoyed',
                        'cat_thought': '（无知的人类，竟敢亵渎神体！）', 'choices': {'A': {'text': '', 'effect': {}},
                                                                      'B': {'text': '重新开始',
                                                                            'effect': {'next_stage': 'restart'}},
                                                                      'C': {'text': '退出游戏',
                                                                            'effect': {'next_stage': 'quit'}}}},
    'ending_annoyed_by_pestering': {'text': f'你反复的试探让【{cat_name}】失去了所有耐心，它不耐烦地“喵！”了一声，转身消失在了黑暗中。', 'mood': 'annoyed',
                                    'cat_thought': '（烦死了！）', 'choices': {'A': {'text': '', 'effect': {}},
                                                                         'B': {'text': '重新开始',
                                                                               'effect': {'next_stage': 'restart'}},
                                                                         'C': {'text': '退出游戏',
                                                                               'effect': {'next_stage': 'quit'}}}}
}

# --- 界面布局 ---
# 改动：在进度条上方增加了一个用于显示“内心戏”的Text元素
layout = [
    [sg.Image(data=image_data['neutral'], key='--CAT_IMAGE--')],
    [sg.Text('', key='--CAT_THOUGHT--', font=('Helvetica', 11, 'italic'), text_color='grey', size=(50, 2),
             justification='c')],
    [sg.ProgressBar(100, orientation='h', size=(30, 20), key='--AFFECTION_BAR--',
                    bar_color=('MediumPurple', 'lightgrey'))],
    [sg.Text('好感度', font=('Helvetica', 10), key='--AFFECTION_TEXT--')],
    [sg.Text(size=(50, 3), key='--STORY_TEXT--', font=('Helvetica', 12))],
    [sg.Button('', key='A', size=(20, 2)), sg.Button('', key='B', size=(20, 2)), sg.Button('', key='C', size=(20, 2))]
]

window = sg.Window(f'与【{cat_name}】的奇遇', layout, element_justification='c', finalize=True)


# --- 核心游戏循环 ---
def update_ui(state):
    stage_info = story_data[state['stage']]
    if state['affection'] < 0: state['affection'] = 0
    if state['affection'] > 100: state['affection'] = 100
    window['--AFFECTION_BAR--'].update(state['affection'])
    window['--AFFECTION_TEXT--'].update(f"好感度: {state['affection']}")

    if state['affection'] >= 80:
        state['cat_mood'] = 'happy'  # 提高开心阈值
    elif state['affection'] <= 20:
        state['cat_mood'] = 'annoyed'  # 降低生气阈值
    else:
        state['cat_mood'] = 'neutral'
    final_mood = stage_info.get('mood', state['cat_mood'])
    window['--CAT_IMAGE--'].update(data=image_data[final_mood])

    window['--STORY_TEXT--'].update(stage_info['text'])
    # 改动：更新内心戏文本
    window['--CAT_THOUGHT--'].update(stage_info.get('cat_thought', ''))

    choices = stage_info.get('choices', {})
    for key in ['A', 'B', 'C']:
        if key in choices and choices[key].get('text'):
            window[key].update(choices[key]['text'], visible=True)
        else:
            window[key].update(visible=False)


update_ui(game_state)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    current_stage_info = story_data[game_state['stage']]
    if 'choices' not in current_stage_info or event not in current_stage_info['choices']:
        continue

    # --- 改动：Bug修复逻辑 ---
    # 如果在 'approach_gently' 阶段点击了 'A' (再试一次)
    if game_state['stage'] == 'approach_gently' and event == 'A':
        game_state['approach_attempts'] += 1
        # 如果尝试次数过多
        if game_state['approach_attempts'] >= 2:
            game_state['stage'] = 'ending_annoyed_by_pestering'
            game_state['affection'] -= 15  # 额外惩罚
            update_ui(game_state)
            continue  # 跳过本次循环的后续部分，直接更新UI到新结局
    # --------------------------

    choice_effect = current_stage_info['choices'][event]['effect']
    next_stage = choice_effect.get('next_stage')

    if next_stage == 'quit':
        break

    if next_stage == 'restart':
        cat_name = game_state['cat_name']
        game_state = {'affection': 50, 'stage': 'start', 'cat_mood': 'neutral', 'cat_name': cat_name,
                      'approach_attempts': 0}
        story_data['start']['text'] = f'一只叫【{cat_name}】的猫咪出现在你家门口，警惕地看着你。'
    elif next_stage:  # 确保有 next_stage 才更新
        game_state['affection'] += choice_effect.get('affection', 0)
        game_state['stage'] = next_stage

    update_ui(game_state)

window.close()
"""
