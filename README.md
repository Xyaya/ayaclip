# AyaClip

## 使用方法：

### 〇 打开 https://clip.ay1.us/web 直接粘贴文本，点击提交上传
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

### 〇 在文件地址后接文件格式或语言名称，可以高亮显示
如：https://clip.ay1.us/f/main/py

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
fcitx5-diagnose | clip5
clip5 < /etc/pacman.conf
```