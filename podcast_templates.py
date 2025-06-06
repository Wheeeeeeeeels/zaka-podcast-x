"""
热门播客模板模块

提供市场上流行的播客模板和风格，用于生成爆款播客内容
"""

class PodcastTemplates:
    # 热门播客风格类型
    PODCAST_STYLES = {
        "知识型": {
            "description": "深度解析各领域知识，类似《知乎日报》、《罗辑思维》风格",
            "tone": "专业、权威、深入浅出",
            "structure": [
                "引入问题或现象",
                "分析问题本质",
                "提供专业见解",
                "举例说明",
                "总结观点"
            ],
            "prompt_template": """
            请以专业的知识分享播客风格，创作一期关于{topic}的内容。
            要求：
            1. 以清晰的问题引入，吸引听众注意
            2. 分析{topic}的核心要素和原理
            3. 提供3-5个关键知识点，每个知识点需深入解析
            4. 使用生动的案例或比喻解释复杂概念
            5. 语言风格要专业但平易近人
            6. 结尾提供实用建议或思考问题
            """
        },
        
        "故事型": {
            "description": "讲述引人入胜的故事，类似《故事FM》、《一千零一夜》风格",
            "tone": "温暖、私密、沉浸式",
            "structure": [
                "悬念开场",
                "主角介绍",
                "情节铺陈",
                "冲突展开",
                "情感高潮",
                "故事结局",
                "感悟分享"
            ],
            "prompt_template": """
            请以沉浸式故事播客风格，创作一期关于{topic}的内容。
            要求：
            1. 以悬念或富有画面感的场景开场
            2. 塑造有特点的人物形象
            3. 构建起伏有致的情节
            4. 设置情感共鸣点和转折点
            5. 语言风格要温暖、私密、富有画面感
            6. 结尾分享故事带来的思考或感悟
            """
        },
        
        "对话型": {
            "description": "模拟访谈对话，类似《十三邀》、《变形记》风格",
            "tone": "轻松、幽默、思辨",
            "structure": [
                "嘉宾介绍",
                "热场话题",
                "核心问题探讨",
                "观点交锋",
                "个人经历分享",
                "观点总结",
                "未来展望"
            ],
            "prompt_template": """
            请以对话访谈播客风格，创作一期与{topic}领域专家的对话内容。
            要求：
            1. 设置主持人和嘉宾两个角色
            2. 主持人提问要犀利、专业、引发思考
            3. 嘉宾回答要有深度、个人见解和实践经验
            4. 对话要有张力和交锋点
            5. 语言风格要自然、幽默、富有个性
            6. 通过对话展现{topic}的多个维度和观点
            """
        },
        
        "商业财经": {
            "description": "分析商业趋势和案例，类似《得到》、《创业内幕》风格",
            "tone": "客观、数据驱动、洞察力强",
            "structure": [
                "市场动态引入",
                "核心数据分析",
                "案例解读",
                "趋势预测",
                "投资建议",
                "行动指南"
            ],
            "prompt_template": """
            请以商业财经播客风格，创作一期关于{topic}的市场分析内容。
            要求：
            1. 以最新市场数据或事件开场
            2. 分析{topic}的商业模式或市场规模
            3. 提供2-3个相关企业案例分析
            4. 引用权威数据和研究报告
            5. 语言风格要客观、专业、富有洞察力
            6. 提供具有前瞻性的趋势判断和建议
            """
        },
        
        "生活方式": {
            "description": "探讨日常生活话题，类似《日谈公园》、《反派影评》风格",
            "tone": "亲切、接地气、实用",
            "structure": [
                "生活现象观察",
                "痛点分析",
                "解决方案",
                "实践建议",
                "个人体验分享",
                "互动环节"
            ],
            "prompt_template": """
            请以生活方式播客风格，创作一期关于{topic}的内容。
            要求：
            1. 以日常生活场景或现象开场
            2. 分析{topic}在生活中的常见问题或误区
            3. 提供3-5个实用的解决方案或技巧
            4. 分享个人或他人的真实体验
            5. 语言风格要亲切、幽默、接地气
            6. 设计1-2个与听众的互动问题或话题
            """
        },
                
        "科技新知": {
            "description": "解读前沿科技和数码产品，类似《硅谷101》、《极客电台》风格",
            "tone": "前沿、专业、通俗易懂",
            "structure": [
                "科技新闻导入",
                "技术原理解析",
                "产品评测",
                "行业影响分析",
                "未来展望",
                "个人观点"
            ],
            "prompt_template": """
            请以科技新知播客风格，创作一期关于{topic}的内容。
            要求：
            1. 以最新科技动态或产品发布开场
            2. 解析{topic}的技术原理或创新点
            3. 评测相关产品的优缺点和使用体验
            4. 分析其对行业或生活的影响
            5. 语言风格要专业但通俗易懂，富有科技感
            6. 提供前瞻性的技术发展预测
            """
        }
    }
    
    # 小宇宙热门播客节目
    TRENDING_PODCASTS = [
        {
            "name": "故事FM",
            "style": "故事型",
            "description": "每天讲述一个平凡人的真实故事",
            "topics": ["个人经历", "社会现象", "情感故事", "人生选择"]
        },
        {
            "name": "得到头条",
            "style": "知识型",
            "description": "解读商业和社会热点",
            "topics": ["商业分析", "社会热点", "行业趋势", "知识解读"]
        },
        {
            "name": "声东击西",
            "style": "对话型",
            "description": "关注全球视野下的中国与世界",
            "topics": ["国际关系", "文化差异", "社会现象", "科技趋势"]
        },
        {
            "name": "商业就是这样",
            "style": "商业财经",
            "description": "分析商业现象与案例",
            "topics": ["创业故事", "商业模式", "企业战略", "投资分析"]
        },
        {
            "name": "日谈公园",
            "style": "生活方式",
            "description": "关注都市生活方式与文化",
            "topics": ["城市生活", "文化现象", "社交话题", "消费趋势"]
        },
        {
            "name": "硅谷101",
            "style": "科技新知",
            "description": "专注科技创新与创业",
            "topics": ["科技创新", "创业经验", "数字产品", "行业分析"]
        }
    ]
    
    @staticmethod
    def get_template_by_style(style_name, topic):
        """获取指定风格的播客模板"""
        if style_name in PodcastTemplates.PODCAST_STYLES:
            template = PodcastTemplates.PODCAST_STYLES[style_name]
            prompt = template["prompt_template"].format(topic=topic)
            return {
                "style": style_name,
                "prompt": prompt,
                "structure": template["structure"],
                "tone": template["tone"]
            }
        return None
    
    @staticmethod
    def get_trending_topics():
        """获取当前热门话题"""
        return [
            "元宇宙与虚拟现实的发展",
            "数字游民生活方式",
            "中式茶饮市场爆发",
            "新世代亲子关系",
            "国潮品牌崛起",
            "可持续消费与环保主义",
            "内容创作者经济",
            "人工智能与创意产业",
            "个人数据隐私与安全",
            "后疫情时代的旅行趋势"
        ]
    
    @staticmethod
    def get_popular_formats():
        """获取流行的播客格式"""
        return {
            "单人主讲": "主播独自讲述内容，适合知识分享和故事叙述",
            "双人对谈": "两位主播互相交流，富有对话感和观点碰撞",
            "嘉宾访谈": "邀请领域专家深度对话，分享专业见解",
            "圆桌讨论": "多位嘉宾共同探讨话题，呈现多元观点",
            "现场录制": "在活动或特定场景录制，增加临场感和互动性",
            "故事叙述": "以讲故事方式呈现内容，增强代入感和情感连接"
        } 