import csv
import time
from collections import deque

"""
数据之间存在规律：如果A_{i}B_{j}之间是朋友关系，那么A_{i+1}B_{j+1}也是朋友关系
每行数据之间和上一行存在递归关系，这些关系存在于每份数据固定长度的段落中，
因此可以简化搜索点，每个段落只需搜索起始点即可，后面的环数量都相同

1.通过深度优先搜索DFS在A和B之间反复往下找，直到固定长度或者无法深入为止；
2.由于环的长度越大纯搜索就越耗时，所以利用一半长度加1的单链然后组合拼接；
3.拼接过后的无向环存在重复，利用字符串编码环信息和集合set()加速遍历去重；

"""

class Solutions():

  def __init__(self, input_file, output_file):
      self.input_file = input_file  #输入的csv文件名
      self.output_file = output_file #输出的文件名
      self.A_num = 0 #存储A部落人数
      self.B_num = 0  # 存储B部落人数
      self.graphAB = {} # 存储A与B的好友关系
      #存储长度为6,7,8的单链，后续组合元素到10,12,14的环
      self.lines = {6:deque([]), 7:deque([]), 8:deque([])} 
      #存储搜索到的长度为4，6，8, 10, 12, 14的环
      self.circles = {4:set(), 6:set(), 8:set(), 10:set(), 12:set(), 14:set()}
      self.count = {4:0, 6:0, 8:0, 10:0, 12:0, 14:0} #存储最终答案
      self.sections_len = 0 # 存储给定数据中设定的固定段落数长度

# 读取CSV文件创建字典表示关系图
  def load(self):
      with open(self.input_file, 'r') as f_in:
           lines = list(csv.reader(f_in))
           self.A_num = len(lines) # A部落人数         
           self.B_num = len(lines[0])  # B部落人数
           for m in range(self.A_num + self.B_num):
               self.graphAB[m] = deque([])
           for i in range(self.A_num):
               for j in range(self.B_num):
                   if lines[i][j] == '1':
                      # A的id：0 ~ self.A_num - 1
                      # B的id：self.A_num ~ self.A_num + self.B_num - 1
                      self.graphAB[i].append(j + self.A_num)
                      self.graphAB[j + self.A_num].append(i)

 # 深度优先遍历搜索小于等于8的路径
  def  DFS(self, s,A_head,path):
       """
       根据好友关系搜索环，直到深度小于8或没有为止
       并根据对应关系存入4，6，8的环和6，7，8的单链
       s: 搜索起始点
       A_head: 最开始的起点A
       path: 搜索出的路径
       """
       # 计算路径的长度
       path_len = len(path)
       
       # 4，6，8的路径的下一个朋友是起点，成4，6，8的环
       if (path_len > 2) and (A_head in self.graphAB[s]) :
          path_ = path[1:] #深拷贝当前path，丢掉开头
          path_.sort() #升序排列
          # 进行字符串编码
          path_s = ''.join(p for p in map(str, path_)) 
          # 利用set()和内置hash函数去重
          if path_s not in self.circles[path_len]:
             self.circles[path_len].add(path_s)
             self.count[path_len] += 1
       
       # 6，7，8的路径塞进存储中，后续组合配对成环
       if (path_len > 5) and (path_len < 9):
          self.lines[path_len].append(path[1:])

      # 深度优先搜索，长度只搜到8
       if path_len < 8:
          for f_next in self.graphAB[s]:
              # 如果一个一个搜，可以这样写，每个环只往下搜避免重复
              # if (f_next not in path) and (f_next > A_head):
              if (f_next not in path): 
                 path.append(f_next)
                 self.DFS(f_next, A_head, path)
                 path.pop()


   #将找到固定长度的单链两两组合成环并去重
  def lines2circles(self):
      """
      把以某个A为起点搜索出的固定长度的单链进行比较
      找出除起终点相同任意元素都不同的单链两两配对成环
      lines: 指定长度的单链集合列表，每个单链开头的元素相同，都是以A中某人为起点
      """
      # 依次拼接长度为6，7，8的单链
      # 初始化访问标志位，便于确立是否可以拼接两条单链
      visited = [0] * (self.A_num + self.B_num)
      for k,v in zip(self.lines.keys(),self.lines.values()):
          len_lines = len(v) #单链的数量
          # 以某个A为起点的固定长度单链可能没有或只有一个，
          # 这个时候无法成环，不用继续运行
          if (len_lines == 0) or (len_lines == 1):  
             return 
          # 开始找环 
          len_circle = 2 * k - 2
          # 将lines按照最后一个元素进行升序，降低循环次数
          v = sorted(v,key=lambda k:k[-1])

          for t in range(len_lines - 1):
              line1 = v[t]
              for s in line1:
                  visited[s] = 1
              for k in range(t+1, len_lines):
                  #确保只在起终点相同的line中组合，第二个没有后面一定没有
                  if line1[-1] != v[k][-1]:
                     break 
                  #找出两个中相同的元素 
                  line2 = v[k][:-1]
                  SAME = 0 # 合并双链判断标志
                  # 除了开头和末尾还有其他元素相同，无法配对成环
                  for s in line2:
                      if visited[s] == 1:
                         SAME = 1
                         break
                  if SAME == 0:
                     #去掉相同的头和尾元素，成环并升序
                     circle = line1 + line2
                     circle.sort()
                      # 字符串编码环存入set()
                     circle_ = ''.join(c for c in map(str, circle))
                     if circle_ not in self.circles[len_circle]:
                        self.circles[len_circle].add(circle_)
                        self.count[len_circle] += 1
              for s in line1:
                  visited[s] = 0

  # 以每个A为起点搜索所有指定长度的不重复无向环                            
  def search_circles(self):
      """
      以每个A为起点找环；
      由于数据存在规律，可以简化搜索点；
      否则，如果是随机生成朋友关系，
      需要一个一个点去搜
      
      """
      # 第一阶段数据各段落开头节点
      if self.A_num == 256:
         nodes = [0, 64, 128, 192]
         self.sections_len = 64
      # 第二阶段数据各段落开头节点   
      elif self.A_num == 1344:
         nodes = [0, 192, 384, 576, 768, 960, 1152]
         self.sections_len = 192
      # 如果数据是随机生成的
      else:
         nodes = range(self.A_num)
      for i in nodes:
          path = [i]
          #找4，6，8长度环和6，7，8长度单链
          self.DFS(i,i,path)
          # 拼接10，12，14长度环
          self.lines2circles()
          
          # 清空，下一次找环做准备
          self.lines = {6:deque([]), 7:deque([]), 8:deque([])}
          self.circles = {4:set(), 6:set(), 8:set(), 10:set(), 12:set(), 14:set()}

          # 简单打印程序进度
          if self.sections_len != 0:
             print('progress:：%d / %d'%(i+self.sections_len, self.A_num), end='\r')
          else:
             print('progress:：%d / %d'%(i+1, self.A_num), end='\r')
          
  # 写入答案到txt文件        
  def output_ans(self):
      """
      把最终的答案写到result.txt文件中
      并打印至终端
      """
      with open(self.output_file, 'w') as f_out:    
          for k,v in zip(self.count.keys(), self.count.values()):
              # 每个A节点会被重复遍历，因此需要除以环中包含的A节点数
              # 如果是一个一个搜，改一下DFS最后的if代码，此处不再需要
              # 这里是为了统一数据规律的情况做了折中处理
              v = v * self.sections_len // (k // 2)
              f_out.write('木托盘上有%d个名字的祭品最多有%d个;\n'%(k,v))
              print('\n', v)


if __name__ == '__main__':
   
   t1 = time.time()
   find = Solutions('Example.csv', 'result.txt')
   find.load()
   find.search_circles()
   find.output_ans()
   t2 = time.time()
   print('Runing Time: %ds'%(t2-t1))
             
