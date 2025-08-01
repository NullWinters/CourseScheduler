# DHU Course Scheduler

## 文件清单

* main.py 主程序
* src/CourseList.json 可选课程列表
* res/* 排课结果
* config/config.json 可调参数

运行main.py后res下将生成排课结果\
以总学分最大原则排课\
由于引入了随机算法，可尝试运行多次求得最佳课表\
可在config.json中调整随机算法的参数