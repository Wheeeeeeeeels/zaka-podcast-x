class PodcastError(Exception):
    """播客生成基础异常类"""
    pass

class ContentGenerationError(PodcastError):
    """内容生成错误"""
    pass

class AudioGenerationError(PodcastError):
    """音频生成错误"""
    pass

class PublishingError(PodcastError):
    """发布错误"""
    pass

class ConfigurationError(PodcastError):
    """配置错误"""
    pass

class APIError(PodcastError):
    """API调用错误"""
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response 