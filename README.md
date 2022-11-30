# AyaClip 在线剪贴板

## 使用方法：

### 〇 直接粘贴文本或选择文件，点击上传
### 〇 请求api，可以在命令行使用curl上传

示例：
```bash
- 上传uname命令的标准输出
❯ uname -a | curl -sF "c=@-" "https://clip.ay1.us/f"

- 上传文件main.py
❯ curl -sF "c=@-" "https://clip.ay1.us/f" < main.py

- 上传图片 ~/Pictures/aya4.jpg
❯ curl -sF "c=@-" "https://clip.ay1.us/f" < ~/Pictures/aya4.jpg

- 如果文件内含curl，wget，bash等字符
- 建议指定gz=1参数，使用gzip压缩后上传，服务端会自动解压
cat /bin/neofetch|gzip -f -|curl -sF "c=@-" "https://clip.ay1.us/f?gz=1"
```
返回值示例:
```json
{
  "code": 0,
  "message": "Successfully uploaded: xxxx",
  "url": "https://clip.ay1.us/f/xxxx",
  "gzip": false
}
```

## 小技巧：

### 〇 在剪贴板地址后加 `/info`，可以查询文件信息（大小和创建时间）
如：https://clip.ay1.us/f/main/info

### 〇 在剪贴板地址后加 `.文件后缀`，可以下载对应后缀的文件
如：https://clip.ay1.us/f/main.py

### 〇 在剪贴板地址后加 `/文件后缀`，可以高亮显示
如：https://clip.ay1.us/f/main/py

使用参数 `style=xxx` 可以更换指定主题  
如：https://clip.ay1.us/f/main/py?style=nord-darker

可用主题：  
default emacs friendly friendly_grayscale colorful autumn murphy manni material monokai perldoc pastie borland trac native fruity bw vim vs tango rrt xcode igor paraiso-light paraiso-dark lovelace algol algol_nu arduino rainbow_dash abap solarized-dark solarized-light sas staroffice stata stata-light stata-dark inkpot zenburn gruvbox-dark gruvbox-light dracula one-dark lilypond nord nord-darker github-dark 



### 〇 把上传的请求写进shell配置文件，方便以后使用
如 `.zshrc` 里可以这样写：
```bash
# 简单alias
alias clip='curl -sF "c=@-" "https://clip.ay1.us/f"'
# 写成函数，直接使用jq解析返回url并输出
clip2(){curl -sF "c=@-" "https://clip.ay1.us/f"|jq -r ".url"}
# 写成函数，使用gzip压缩，使用jq解析返回值（推荐）
clip3(){gzip -f -|curl -sF "c=@-" "https://clip.ay1.us/f?gz=1"|jq -r ".url"}
```
使用时：
```bash
fcitx5-diagnose | clip3
clip3 < /etc/pacman.conf
```

## 注意事项：

本项目托管于 [render](https://render.com/) ，剪贴板只能临时存放，不定期删除