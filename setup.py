from setuptools import setup, find_packages

setup(
    name="zaka-podcast",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.12.0",
        "python-dotenv>=1.0.0",
        "gTTS>=2.4.0",
        "pydub>=0.25.1",
        "pyaudio>=0.2.14",
        "numpy>=1.26.4",
        "librosa>=0.10.1",
        "requests>=2.31.0",
        "python-slugify>=8.0.1",
        "aiohttp>=3.9.3",
        "tqdm>=4.66.2",
        "python-dateutil>=2.8.2",
        "pytz>=2024.1"
    ],
    python_requires=">=3.8",
) 