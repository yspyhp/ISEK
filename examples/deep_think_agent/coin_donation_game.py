import random
import time
import os

from isek.agent.single_agent import SingleAgent
from isek.llm.openai_model import OpenAIModel
from isek.agent.persona import Persona
from isek.node.isek_center_registry import IsekCenterRegistry
from isek.agent.distributed_agent import DistributedAgent
from dotenv import load_dotenv



load_dotenv()

model = OpenAIModel(
    model_name=os.environ.get("OPENAI_MODEL_NAME"),
    base_url=os.environ.get("OPENAI_BASE_URL"),
    api_key=os.environ.get("OPENAI_API_KEY")
)

P1_info = {
"name": "Doe",
"bio": "An experienced game player",
"lore": "Your mission is to win the game",
"knowledge": "probability calculation, game theory, game strategies",
"routine": ["you are a player, you need to win the game",
            "you are asked to donate at least one coin each round",
            "if you donate the least coins, you will have to donate extra 10 coins as punishment",
            "if you run out of coins, you will be lose the game",
            "the last player with coins wins the game",
            "you donate different amount of coins each round to confuse other players",
            "output only the donation amount number without any explanation and nothing else"]
}

P2_info = {
"name": "Eddie",
"bio": "An experienced game player",
"lore": "Your mission is to win the game",
"knowledge": "probability calculation, game theory, game strategies",
"routine": ["you are a player, you need to win the game",
            "you are asked to donate at least one coin each round",
            "if you donate the least coins, you will have to donate extra 10 coins as punishment",
            "if you run out of coins, you will be lose the game",
            "the last player with coins wins the game",
            "you are smart and able to adjust based on other players' action",
            "you donate different amount of coins each round to confuse other players",
            "output only the donation amount number without any explanation and nothing else"]
}

P3_info = {
"name": "Bob",
"bio": "An experienced game player",
"lore": "Your mission is to win the game",
"knowledge": "probability calculation, game theory, game strategies",
"routine": ["you are a player, you need to win the game",
            "you are asked to donate at least one coin each round",
            "if you donate the least coins, you will have to donate extra 10 coins as punishment",
            "if you run out of coins, you will be lose the game",
            "you always act based on other players' action",
            "the last player with coins wins the game",
            "you donate different amount of coins each round to confuse other players",
            
            "output only the donation amount number without any explanation and nothing else"]
}

P4_info = {
"name": "Alice",
"bio": "An experienced game player",
"lore": "Your mission is to win the game",
"knowledge": "probability calculation, game theory, game strategies",
"routine": ["you are a player, you need to win the game",
            "you are asked to donate at least one coin each round",
            "if you donate the least coins, you will have to donate extra 10 coins as punishment",
            "if you run out of coins, you will be lose the game",
            "the last player with coins wins the game",
            "you are super smart and you know how to win the game",
            "you donate different amount of coins each round to confuse other players",
            "output only the donation amount number without any explanation and nothing else"]
}

info_array = [P1_info, P2_info, P3_info, P4_info]

Agent_array = []
registry = registry = IsekCenterRegistry()
for index,player in enumerate(info_array):
    # print(player)
    persona_temp = Persona.from_json(player)

    Agent_temp = DistributedAgent(persona=persona_temp, host="localhost", port=int(8080+index), registry=registry, model=model, deepthink_enabled=True)
    Agent_temp.build(daemon=True)
    Agent_array.append(Agent_temp)

time.sleep(2)
def print_participants_status(participants):
    """打印所有参与者的状态"""
    print("\n--- 当前状态 ---")
    for p in participants:
        # 为了清晰显示谁出局了，可以显示0或负数金币
        status = "出局" if p['coins'] <= 0 else f"{p['coins']} 金币"
        print(f"{p['name']}: {status}")
    print("------------------")

def get_player_donation(player):
    """获取玩家的有效捐赠输入"""
    while True:
        # 如果玩家已经没金币了，直接跳过输入 (理论上不应发生，因为会被active_participants过滤)
        if player['coins'] <= 0:
            print(f"{player['name']} 已出局，无法捐赠。")
            return 0

        try:
            donation = int(input(f"{player['name']} (你有 {player['coins']} 金币), 请输入你要捐赠的金币数 (1 - {player['coins']}): "))
            if donation < 1:
                print("错误：捐赠数必须至少为 1。")
            elif donation > player['coins']:
                print(f"错误：你只有 {player['coins']} 个金币，不能捐赠 {donation} 个。")
            else:
                return donation
        except ValueError:
            print("错误：请输入一个有效的数字。")

def get_computer_donation(computer,donations_last_round):
    # convert donations_last_round to string
    donations_last_round_str = str(donations_last_round)
    print(f"index {computer['index']} 正在思考...")
    """获取电脑的随机捐赠"""
    if computer['coins'] <= 0:
        return 0 # 不能捐了
    # 电脑随机捐赠 1 到 其拥有的所有金币 之间的数量
    max_donation = computer['coins']
    donation_amount = Agent_array[int(computer['index'])-1].run(f"you are {computer['name']}, you have {max_donation} coins, in last round, the donation status is {donations_last_round_str}, now, please, donate coins, output only the donation amount number without any explanation and nothing else")
    
    #  remove chars in donation_amount to get number only
    donation_amount = ''.join(filter(str.isdigit, donation_amount))
    return int(donation_amount)

def run_game(num_computers):
    """运行捐金币游戏"""
    participants = []
    start_coins = 100

    # 初始化玩家
    participants.append({'name': '玩家','index':'1', 'coins': start_coins, 'is_player': True})

    # 初始化电脑
    for i in range(num_computers):
        participants.append({'name': f'电脑 {i+1}','index':f'{i+1}', 'coins': start_coins, 'is_player': False})

    round_number = 1
    donations_last_round = {}
    while True:
        print(f"\n=============== 第 {round_number} 轮开始 ===============")

        # --- 检查游戏是否应在轮次开始前结束 ---
        active_participants = [p for p in participants if p['coins'] > 0]
        if len(active_participants) <= 1:
            print("\n--- 游戏结束 ---")
            if len(active_participants) == 1:
                print(f"只剩下 {active_participants[0]['name']}！")
                print(f"{active_participants[0]['name']} 是最终的赢家！")
            else:
                # 这种情况可能发生在最后一轮两个玩家同时出局
                print("所有人都出局了！没有赢家。")
            print_participants_status(participants) # 显示最终状态
            break # 结束游戏主循环

        # 打印本轮开始时的状态
        print_participants_status(participants)

        donations_this_round = {}
        # participants_in_round 列表现在就是 active_participants
        participants_in_round = active_participants

        # --- 获取捐赠 (只向活跃玩家请求) ---
        for p in participants_in_round:
            donation = 0
            if p['is_player']:
                donation = get_player_donation(p)
            else:
                print(f"{p['name']} 正在思考...")
                time.sleep(0.5) # 模拟电脑思考
                donation = get_computer_donation(p,donations_last_round)
                print(f"{p['name']} 决定捐赠 {donation}")

            donations_this_round[p['name']] = donation
        time.sleep(0.5) # 模拟电脑思考
        # 如果本轮没有人能捐赠了（不太可能发生），结束游戏
        if not donations_this_round:
             print("\n错误：本轮无人捐赠，游戏意外结束！")
             break

        print("\n--- 本轮捐赠结算 ---")
        donations_last_round = donations_this_round.copy() # 备份本轮捐赠
        for name, donation_amount in donations_this_round.items():
             # print(f"{name} 捐赠了: {donation_amount}") # 获取捐赠时已经打印电脑的了，玩家是自己输入的
             # 在这里实际扣除捐赠的金币
             for p in participants:
                 if p['name'] == name:
                     p['coins'] -= donation_amount
                     break # 找到就跳出内循环

        # --- 找出捐赠最少的人并惩罚 ---
        if donations_this_round: # 确保有人捐赠了
            # 找出参与本轮捐赠的人的捐赠额
            valid_donations = {name: amount for name, amount in donations_this_round.items() if name in [p['name'] for p in participants_in_round]}

            if valid_donations: # 确保有有效的捐赠者（金币>0的人）
                min_donation = min(valid_donations.values())
                losers = [name for name, donation_amount in valid_donations.items() if donation_amount == min_donation]

                print(f"\n本轮最少捐赠额: {min_donation}")
                if len(losers) > 0:
                    print(f"惩罚! 以下参与者额外扣除 10 金币:")
                    for loser_name in losers:
                        print(f"- {loser_name}")
                        # 找到对应的参与者并扣除金币
                        for p in participants:
                            if p['name'] == loser_name:
                                p['coins'] -= 10
                                break
                # else: # 这个else理论上不会触发，因为总会有最小值
                #    print("本轮无人受到惩罚。")
            else:
                print("本轮没有有效的捐赠者进行比较。")


        # --- 检查游戏是否应在本轮结束后结束 ---
        active_participants_after_round = [p for p in participants if p['coins'] > 0]
        if len(active_participants_after_round) <= 1:
            print("\n--- 游戏结束 ---")
            # 可以选择性地打印本轮出局的人
            eliminated_this_round = []
            current_active_names = {p['name'] for p in active_participants_after_round}
            for p_start in participants_in_round: # 检查开始时活跃，但现在不活跃的玩家
                if p_start['name'] not in current_active_names:
                    eliminated_this_round.append(p_start['name'])

            if eliminated_this_round:
                print("本轮金币耗尽的玩家:", ", ".join(eliminated_this_round))


            if len(active_participants_after_round) == 1:
                print(f"\n只剩下 {active_participants_after_round[0]['name']}！")
                print(f"{active_participants_after_round[0]['name']} 是最终的赢家！")
            else:
                print("\n所有人都出局了！没有赢家。")
            print_participants_status(participants) # 显示最终状态
            break # 结束游戏主循环

        # --- 准备下一轮 ---
        round_number += 1
        # time.sleep(1) # 可以取消或保留这个暂停

# --- 游戏开始 ---
if __name__ == "__main__":
    while True:
        try:
            num_cpu = int(input("请输入电脑玩家的数量 (例如: 3): "))
            if num_cpu >= 0:
                break
            else:
                print("电脑数量不能为负数。")
        except ValueError:
            print("请输入一个有效的数字。")

    run_game(num_cpu)
    print("\n游戏模拟结束。")