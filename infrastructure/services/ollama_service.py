import httpx
import json
from typing import Optional, Dict, Any, List
import logging


class OllamaService:
    """Ollama AI模型服务"""
    
    def __init__(self, ollama_url: str, default_model: str = "llama3"):
        self.ollama_url = ollama_url
        self.default_model = default_model
        self.logger = logging.getLogger(__name__)
    
    async def generate_content(
        self,
        prompt: str,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        生成AI内容
        
        Args:
            prompt: 提示词
            model: 模型名称，默认为配置的默认模型
            options: 模型选项
            
        Returns:
            生成的内容
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": model or self.default_model,
                    "prompt": prompt,
                    "stream": False
                }
                
                if options:
                    payload["options"] = options
                
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    self.logger.error(
                        f"Ollama API error: {response.status_code} - {response.text}"
                    )
                    return None
                    
        except httpx.RequestError as e:
            self.logger.error(f"Ollama request error: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Ollama response parse error: {e}")
            return None
    
    async def generate_video_title(
        self,
        video_description: str,
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        生成视频标题（异步版本）
        
        Args:
            video_description: 视频内容描述
            model: 模型名称
            
        Returns:
            生成的标题
        """
        prompt = f"""
        请为以下视频内容生成一个吸引人的短视频标题（15-20字）：
        
        视频内容：{video_description}
        
        要求：
        1. 标题要简洁有力，能快速抓住观众注意力
        2. 使用热门关键词，提高搜索曝光
        3. 包含emoji表情符号增加吸引力
        4. 直接输出标题，不要有任何引言或解释
        """
        
        return await self.generate_content(prompt, model)
    
    def generate_video_title_sync(
        self,
        video_description: str,
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        生成视频标题（同步版本）
        
        Args:
            video_description: 视频内容描述
            model: 模型名称
            
        Returns:
            生成的标题
        """
        import asyncio
        
        prompt = f"""
        请为以下视频内容生成一个吸引人的短视频标题（15-20字）：
        
        视频内容：{video_description}
        
        要求：
        1. 标题要简洁有力，能快速抓住观众注意力
        2. 使用热门关键词，提高搜索曝光
        3. 包含emoji表情符号增加吸引力
        4. 直接输出标题，不要有任何引言或解释
        """
        
        return asyncio.run(self.generate_content(prompt, model))
    
    async def generate_video_description(
        self,
        video_description: str,
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        生成视频描述（异步版本）
        
        Args:
            video_description: 视频内容描述
            model: 模型名称
            
        Returns:
            生成的描述
        """
        prompt = f"""
        请为以下视频内容生成一个详细的短视频描述（100-150字）：
        
        视频内容：{video_description}
        
        要求：
        1. 描述要吸引人，激发观众观看兴趣
        2. 包含3-5个相关话题标签（用#开头）
        3. 语言口语化，符合短视频平台风格
        4. 内容要完整，涵盖视频的主要亮点
        """
        
        return await self.generate_content(prompt, model)
    
    def generate_video_description_sync(
        self,
        video_description: str,
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        生成视频描述（同步版本）
        
        Args:
            video_description: 视频内容描述
            model: 模型名称
            
        Returns:
            生成的描述
        """
        import asyncio
        
        prompt = f"""
        请为以下视频内容生成一个详细的短视频描述（100-150字）：
        
        视频内容：{video_description}
        
        要求：
        1. 描述要吸引人，激发观众观看兴趣
        2. 包含3-5个相关话题标签（用#开头）
        3. 语言口语化，符合短视频平台风格
        4. 内容要完整，涵盖视频的主要亮点
        """
        
        return asyncio.run(self.generate_content(prompt, model))
    
    async def generate_video_tags(
        self,
        video_description: str,
        num_tags: int = 5,
        model: Optional[str] = None
    ) -> Optional[List[str]]:
        """
        生成视频标签（异步版本）
        
        Args:
            video_description: 视频内容描述
            num_tags: 标签数量
            model: 模型名称
            
        Returns:
            生成的标签列表
        """
        prompt = f"""
        请为以下视频内容生成{num_tags}个相关的短视频标签：
        
        视频内容：{video_description}
        
        要求：
        1. 标签要与视频内容高度相关
        2. 包含1-2个热门大标签和3-4个精准小标签
        3. 每个标签控制在2-5个字
        4. 直接输出标签列表，用逗号分隔，不要有任何其他内容
        """
        
        result = await self.generate_content(prompt, model)
        if result:
            # 解析标签列表
            tags = [tag.strip() for tag in result.split(",") if tag.strip()]
            return tags[:num_tags]
        return []
    
    def generate_video_tags_sync(
        self,
        video_description: str,
        num_tags: int = 5,
        model: Optional[str] = None
    ) -> Optional[List[str]]:
        """
        生成视频标签（同步版本）
        
        Args:
            video_description: 视频内容描述
            num_tags: 标签数量
            model: 模型名称
            
        Returns:
            生成的标签列表
        """
        import asyncio
        
        prompt = f"""
        请为以下视频内容生成{num_tags}个相关的短视频标签：
        
        视频内容：{video_description}
        
        要求：
        1. 标签要与视频内容高度相关
        2. 包含1-2个热门大标签和3-4个精准小标签
        3. 每个标签控制在2-5个字
        4. 直接输出标签列表，用逗号分隔，不要有任何其他内容
        """
        
        result = asyncio.run(self.generate_content(prompt, model))
        if result:
            # 解析标签列表
            tags = [tag.strip() for tag in result.split(",") if tag.strip()]
            return tags[:num_tags]
        return []
    
    async def analyze_video_content(
        self,
        video_path: str,
        model: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        分析视频内容（模拟，实际需要视频理解模型）
        
        Args:
            video_path: 视频文件路径
            model: 模型名称
            
        Returns:
            视频内容分析结果
        """
        # 注意：实际的视频内容分析需要更复杂的模型和处理
        # 这里只是一个简化的模拟实现
        prompt = f"""
        请分析以下视频文件路径对应的视频内容，并提供分析结果：
        
        视频路径：{video_path}
        
        请提供以下信息：
        1. 视频可能的主题和内容类型
        2. 视频的关键亮点和吸引人的地方
        3. 适合的目标受众
        
        注意：这是一个模拟分析，实际应用中需要使用视频理解模型
        """
        
        result = await self.generate_content(prompt, model)
        if result:
            # 解析结果
            lines = result.strip().split("\n")
            analysis = {
                "theme": lines[0] if len(lines) > 0 else "",
                "highlights": lines[1] if len(lines) > 1 else "",
                "audience": lines[2] if len(lines) > 2 else ""
            }
            return analysis
        return None
    
    async def generate_complete_video_metadata(
        self,
        video_description: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成完整的视频元数据
        
        Args:
            video_description: 视频内容描述
            model: 模型名称
            
        Returns:
            包含标题、描述、标签的元数据字典
        """
        # 并行生成标题、描述和标签
        title_task = self.generate_video_title(video_description, model)
        description_task = self.generate_video_description(video_description, model)
        tags_task = self.generate_video_tags(video_description, model=model)
        
        # 等待所有任务完成
        title = await title_task
        description = await description_task
        tags = await tags_task
        
        return {
            "title": title or "未命名视频",
            "description": description or "暂无描述",
            "tags": tags or []
        }