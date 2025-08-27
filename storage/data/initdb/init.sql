CREATE TABLE IF NOT EXISTS system_bubble (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT,
    x FLOAT,
    y FLOAT,
    active BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS system_ip(
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip TEXT,
    count INTEGER,
    first_time INTEGER
);

CREATE TABLE IF NOT EXISTS system_joke(
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT
);

CREATE TABLE IF NOT EXISTS system_panel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT,
    description TEXT,
    url TEXT,
    tasks TEXT
);

CREATE TABLE IF NOT EXISTS system_timeline (
    id INT AUTO_INCREMENT PRIMARY KEY,
    node_id INTEGER,
    date DATE,
    event TEXT,
    tag TEXT
);

CREATE TABLE IF NOT EXISTS system_wiki (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    group_name VARCHAR(255),
    content Text,
    sort INT
);


CREATE TABLE IF NOT EXISTS user_information (
    id INT AUTO_INCREMENT PRIMARY KEY,
    qq BIGINT UNIQUE,
    nickname VARCHAR(50),
    codename VARCHAR(50),
    name VARCHAR(50),
    grade varchar(50),
    gender ENUM('男', '女') DEFAULT NULL,
    major VARCHAR(100),
    student_id VARCHAR(20),
    phone VARCHAR(20),
    political_status VARCHAR(50),
    hometown VARCHAR(100),
    card_number VARCHAR(20),
    card_id VARCHAR(30)
);

CREATE TABLE user_media (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filepath VARCHAR(255) UNIQUE,
    media_id VARCHAR(256),
    wechat DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    media_json JSON,
    qq DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    media_url JSON
);

CREATE TABLE IF NOT EXISTS user_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user VARCHAR(255) UNIQUE,
    status TEXT,
    information TEXT
);

CREATE TABLE IF NOT EXISTS user_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user BIGINT UNIQUE,
    nickname VARCHAR(255),
    name VARCHAR(255),
    password VARCHAR(255)
);

INSERT INTO system_joke (text) VALUES
('华生：“你怎么知道我要喝三分糖？”
福尔摩斯：“你嘴角有蚂蚁排队，说明糖量不足致死；你手机屏保是‘抗糖宣言’，但手指在‘全糖’选项上有划痕……”
华生：“停！我只是今天想放纵！”
福尔摩斯：“……哦，那是我推理错了。”'),
('程序员单膝跪地：“你是我的全局唯一解！”
女友：“那你的前女友呢？”
程序员：“她们是局部最优解，但收敛不到你。”'),
('“先有鸡还是先有蛋？”
哲学家：“先有‘先’这个字。”'),
('数学家向朋友炫耀：「我能用归纳法证明所有人都是光头！」
朋友：「？？？」
数学家：「1个人是光头，假设k个人是光头，那么k+1个人也是光头，证毕。」
朋友：「你漏了归纳基础，第一个人根本不是光头！」
数学家摸头：「啊，我确实是光头。」'),
('警长：“这密室杀人案必须请顶级侦探！”
局长：“不用，把案发现场挂到Airbnb上，写上‘凶宅半价’，凶手会来自首的。”'),
('三个逻辑学家走进酒吧。
酒保问：「三位都要啤酒吗？」
第一个说：「我不知道。」
第二个说：「我也不知道。」
第三个说：「是的，都要。」'),
('女友：“你和前女友纠缠不清是吧？”
男友：“不！我和她的关系是量子态的——你不观测时不存在！”
女友：“那我观测一下你的手机？”
男友：“……系统坍缩了。”'),
('教授：“给猴子一台打字机，迟早打出《莎士比亚全集》！”
学生：“那它们打出‘您访问的网站存在风险’怎么办？”
教授：“……说明猴子当网警了。”'),
('妻子：「你说你爱我，到底有多爱？」
程序员：「我对你的爱，等于我对你的爱加上1。」
妻子：「死循环了是吧？」
（无限递归表白，卒）'),
('老婆：“买颗白菜，顺便带根葱。”
程序员老公：“最优路径是：先到葱摊，因为葱的保质期是白菜的0.3倍；但根据实时人流……”
老婆：“你买了三小时还没回来？！”
老公：“……我在模拟退火算法。”'),
('死者：“我在虚拟世界被杀了！这犯法吗？”
警察：“根据《刑法》第250条，凶手得先证明你是真人。”
死者：“……我微信余额还有3块5！”
警察：“立案了！”'),
('凶手：“我用了完美分尸手法，你绝对找不到证据！”
侦探：“确实，但你把肝扔进了厨余垃圾桶——”
凶手：“所以呢？！”
侦探：“小区垃圾分类奖金被扣了，保洁阿姨供出了你。”'),
('老婆：“买两斤土豆，要表面光滑摩擦系数小的。”
物理学家：“你是要做惯性实验还是炖牛肉？”
老婆：“……要好削皮的。”'),
('凶手：“案发时我在元宇宙挖矿！”
警察：“但你显卡温度记录显示当时在玩《原神》。”
凶手：“……我承认，是我干的。”'),
('客户：“我要一个绝对完美的密室杀人案！”
侦探：“好的，方案是：门没锁，但甲方坚持说它是密室。”');
