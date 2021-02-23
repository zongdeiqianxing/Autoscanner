#### MySimpleScanner
自己折腾的简单扫描器，可以集成开源工具以构建扫描模块，辅助挖洞
目前集成dirsearch JSFinder heartblood iis_shortname_Scan nmap hydra等模块；


```
Usage:
python3 recon.py -u url 
python3 recon.py -f filename        #-f参数使用时，适配OneforAll、subDoaminBrute等域名爆破工具的outut文件；手写域名的文件也可以；
python3 recon.py -d domain          #-d参数使用时，输入主域名后，一键查找子域名、模块扫描。适用于刷src的情形
```


