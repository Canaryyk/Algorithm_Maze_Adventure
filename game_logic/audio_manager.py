"""
音乐管理器 - 处理游戏中的背景音乐和音效播放
"""

import arcade
import config as cfg
from pathlib import Path

class AudioManager:
    """
    音乐管理器类 - 负责游戏中所有音频的播放和管理
    """
    
    def __init__(self):
        """初始化音乐管理器"""
        self.background_music = None
        self.current_background: str | None = None
        self.sound_effects = {}
        self.is_music_enabled = True
        self.is_effects_enabled = True
        
        # 预加载音效文件
        self._load_sound_effects()
    
    def _load_sound_effects(self):
        """预加载所有音效文件到内存中"""
        try:
            for sound_name, sound_path in cfg.MUSIC_PATHS.items():
                if sound_name != "background" and sound_name != "boss_battle":
                    # 只预加载短音效，背景音乐单独处理
                    if Path(sound_path).exists():
                        self.sound_effects[sound_name] = arcade.load_sound(str(sound_path))
                    else:
                        print(f"警告: 音效文件未找到: {sound_path}")
        except Exception as e:
            print(f"加载音效时出错: {e}")
    
    def play_background_music(self, music_type="background"):
        """
        播放背景音乐
        
        Args:
            music_type: 音乐类型 ("background" 或 "boss_battle")
        """
        if not self.is_music_enabled:
            return
        
        # 如果当前已经在播放同样的背景音乐，不需要重新播放
        if self.current_background == music_type and self.background_music:
            return
        
        # 停止当前背景音乐
        self.stop_background_music()
        
        try:
            music_path = cfg.MUSIC_PATHS.get(music_type)
            if music_path and Path(music_path).exists():
                sound = arcade.load_sound(str(music_path))
                if sound:
                    self.background_music = arcade.play_sound(sound, volume=cfg.BACKGROUND_VOLUME)
                    self.current_background = music_type
                    print(f"开始播放背景音乐: {music_type}")
                else:
                    print(f"无法加载音乐文件: {music_path}")
            else:
                print(f"背景音乐文件未找到: {music_path}")
        except Exception as e:
            print(f"播放背景音乐时出错: {e}")
    
    def stop_background_music(self):
        """停止背景音乐"""
        if self.background_music:
            try:
                arcade.stop_sound(self.background_music)
                self.background_music = None
                self.current_background = None
            except Exception as e:
                print(f"停止背景音乐时出错: {e}")
    
    def play_sound_effect(self, effect_name):
        """
        播放音效
        
        Args:
            effect_name: 音效名称
        """
        if not self.is_effects_enabled:
            return
        
        if effect_name in self.sound_effects:
            try:
                arcade.play_sound(self.sound_effects[effect_name], volume=cfg.EFFECT_VOLUME)
            except Exception as e:
                print(f"播放音效 {effect_name} 时出错: {e}")
        else:
            print(f"音效未找到: {effect_name}")
    
    def toggle_music(self):
        """切换背景音乐开/关状态"""
        self.is_music_enabled = not self.is_music_enabled
        if not self.is_music_enabled:
            self.stop_background_music()
        else:
            # 重新开始播放背景音乐，默认使用background，如果有当前音乐则使用当前音乐
            if self.current_background:
                self.play_background_music(self.current_background)
            else:
                self.play_background_music("background")
        print(f"背景音乐: {'开启' if self.is_music_enabled else '关闭'}")
    
    def toggle_effects(self):
        """切换音效开/关状态"""
        self.is_effects_enabled = not self.is_effects_enabled
        print(f"音效: {'开启' if self.is_effects_enabled else '关闭'}")
    
    def set_music_volume(self, volume):
        """设置背景音乐音量 (0.0 - 1.0)"""
        cfg.BACKGROUND_VOLUME = max(0.0, min(1.0, volume))
        if self.background_music:
            # 需要重新播放来应用新音量
            current_music = self.current_background
            self.stop_background_music()
            self.play_background_music(current_music)
    
    def set_effects_volume(self, volume):
        """设置音效音量 (0.0 - 1.0)"""
        cfg.EFFECT_VOLUME = max(0.0, min(1.0, volume))
    
    def cleanup(self):
        """清理音频资源"""
        self.stop_background_music()
        # 清理音效缓存
        self.sound_effects.clear()
        print("音频管理器已清理")

# 全局音频管理器实例
audio_manager = AudioManager() 