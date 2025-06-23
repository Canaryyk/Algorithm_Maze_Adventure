```
Algorithm_Maze_Adventure/
│
├── main.py                 # 游戏主入口：初始化、游戏主循环、场景切换
├── config.py               # 配置文件：屏幕尺寸、颜色、帧率、游戏数值等常量
│
├── game_logic/             # 核心游戏逻辑模块
│   ├── __init__.py
│   ├── player.py             # 玩家类 (Player)：处理移动、状态（生命、金币）、碰撞
│   ├── maze.py               # 迷宫类 (Maze)：存储地图数据、绘制地图、处理地图元素交互
│   ├── ui.py                 # UI界面模块：绘制血条、金币数、提示信息、菜单
│   └── game_state.py         # 游戏状态管理器：管理主菜单、游戏中、游戏结束等状态
│
├── algorithms/             # 核心算法实现模块 (每位成员的核心产出)
│   ├── __init__.py
│   ├── maze_generator.py     # 成员A: 分治法迷宫生成器
│   ├── pathfinding.py        # 成员B: 动态规划最优路径 & 贪心算法实时寻路
│   ├── puzzle_solver.py      # 成员C: 回溯法解谜器
│   └── boss_battle_solver.py # 成员C: 分支限界BOSS战策略求解器
│
├── visualizer/             # 成员D: 算法可视化模块
│   ├── __init__.py
│   ├── path_visualizer.py    # 可视化路径规划过程 (高亮访问节点、最终路径)
│   └── generation_visualizer.py # 可视化迷宫生成过程 (实时绘制墙壁和通道)
│
├── assets/                 # 资源文件夹
│   ├── images/               # 存放图片资源 (墙壁、地板、玩家、金币、陷阱、BOSS等)
│   │   ├── player.png
│   │   ├── wall.png
│   │   └── ...
│   ├── sounds/               # 存放音效和背景音乐
│   │   ├── bgm.mp3
│   │   └── pickup.wav
│   └── fonts/                # 存放自定义字体文件
│       └── pixel_font.ttf
│
├── utils/                  # 工具类模块
│   ├── __init__.py
│   └── map_io.py             # 用于保存和加载迷宫地图文件 (如JSON格式)
│
└── README.md               # 项目说明文件：介绍、如何运行、成员分工等
```