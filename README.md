# 太极图形课S1-大作业-基于广义相对论的光线步进黑洞模拟

## 作业来源
这里采用 Ray Marching 的方式，模拟了无自旋黑洞周围吸积盘（只是一个发光的圆盘，并不真实）看起来的样子。由于黑洞非常大的质量，导致周围的时空发生弯曲，因此不能使用常规的欧式度规来衡量直线，这时候对于无自旋黑洞就需要使用史瓦西度规（对于带有自旋的黑洞，比如星际穿越中的卡冈图雅，则需要用克尔度规，代码的复杂度会上升）。通俗来讲则是：黑洞周围的直线“不直”，光也并不直着走，我们需要根据度规解出测地线方程来判断光走了什么样的路径。

求解测地线方程，以及求克氏符来进行坐标变换是一件繁琐的事情。但史瓦西黑洞具有着球对称性，因此模拟过程可以被简化。光线在具有球对称的度规空间中只会在一个平面内进行步进，于是我们在计算运动时可以将光线进行降维处理，只考虑其所在平面内的变化。在此使用辛欧拉法进行光线位置的更新（似乎使用Runge-Kutta效果会好些，但这里没测试过）。

要注意的是，这里对吸积盘的模拟并不真实，由于真实情况中吸积盘内粒子的运动速度非常快，因此会产生多普勒效应，远离我们的粒子会偏红，靠近我们的粒子会偏蓝。与此同时距离黑洞近的粒子会产生引力红移（这是因为靠近黑洞的物体时间相对于远离黑洞的我们走的更慢，因此发出光的频率比通常显得更低）。在这里并没有考虑光谱上的变化。

参考资料：
[1] _Real-time High-Quality Rendering of Non-Rotating Black Holes_ Eric Bruneton 	arXiv:2010.08735

[2] _Gravitational Lensing by Spinning Black Holes in Astrophysics, and in the Movie Interstellar_ Oliver James, Eugenie von Tunzelmann, Paul Franklin, Kip S. Thorne  arXiv:1502.03808

[3] https://rantonels.github.io/starless/

## 运行方式

#### 运行环境：
[Taichi] version 0.8.1, llvm 10.0.0, commit cc2dd342, win, python 3.9.5

#### 运行：
直接运行main.py即可，如果想要改变摄像机角度以及位置，可在gr_ray_tracing_model.py中的Camera类相应位置进行修改。

## 效果展示
![blackhole demo1](./data/small_angle.png)
![blackhole demo2](./data/side.png)
![blackhole demo3](./data/moving.gif)

## 整体结构

```
-LICENSE
-|data
-README.MD
-main.py
-gr_ray_tracing_model.py
```

## 实现细节：

### 整体流程
1. 高斯矩阵预计算（用来进行高斯模糊，非必要）
2. 创建摄像机与窗口
3. 产生射线
4. 射线进行步进
5. 碰撞以及边界检测
6. 高斯模糊并叠加canvas，产生辉光效果
7. 绘制光追结果至屏幕



# 示例
下面给出一个模版供大家参考，在你提交大作业的时候可以删除示例部分。按上面的要求填写自己大作业的内容。

## 作业来源
布料仿真是计算机图形学中一个重要的仿真场景，在电影和游戏中都有很广泛的应用。一个很经典的布料仿真方法是 [*Large Steps in Cloth Simulation.*](https://www.cs.cmu.edu/~baraff/papers/sig98.pdf) David Baraff, Andrew Witkin. Siggraph 1998. 这也是皮克斯 (Pixar) 动画仿真器 **Fizt** 使用的布料仿真方法。在SCA 2020中有有一篇[论文](https://www.tkim.graphics/FEMBW/)描述了该论文中布料仿真模型对应的FEM形式。

本次大作业就是对Baraff-Witkin布料仿真的实现。在实现过程中，可以了解能量、力和刚度矩阵的计算。除此之外，还可以了解Taichi语言中稀疏矩阵 (Sparse Matrix) 的使用，共轭梯度法 (Conjugate Gradient, CG) 的实现。

## 运行方式
#### 运行环境：
`[Taichi] version 0.8.7, llvm 10.0.0, commit 1c3c705a, osx, python 3.8.8`

#### 运行：
在运行 `implicit_mass_spring_system.py`时，可以通过命令行参数 `-cg` 来控制是否使用 **CG** solver。

- 使用 Direct solver:
`python implicit_mass_spring_system.py`

- 使用 CG solver:
`python implicit_mass_spring_system.py  -cg`


## 效果展示
左侧：Direct solver；右侧： Conjugate Gradient (CG) solver。 
![mass spring demo](./data/direct_vs_cg.gif)

## 整体结构
```
-LICENSE
-|data
-README.MD
-implicit_mass_spring_system.py
```

## 实现细节：
`implicit_mass_spring_system.py`是项目源代码，其中包含一个Cloth类和一个`main`函数。具体公式推导，可以看: [here](https://github.com/taichiCourse01/taichiCourse01/blob/main/material/09_implicit_integration.pdf) (P45-46)。

### 整体流程
1. 布料的初始化
2. 创建一个GUI来显示布料
3. 根据命令行选项更新布料，默认使用 direct solver 来更新布料。可以命令行参数 `-cg` 来使用 CG solver。
4. 在GUI中显示布料

### 布料类
1. [初始化](https://github.com/FantasyVR/taichi_course_final_project/blob/304a32dfa686862adcb54f737ed6970e21fe8d5b/implicit_mass_spring.py#L13)
   - 设置field，确定数据结构
   - 初始化field，设置位置，速度，质量和每个弹簧两个端点索引

2. 布料更新 Direct Solver: [`update_direct(h)`](https://github.com/FantasyVR/taichi_course_final_project/blob/8f79e0026237e75ec3abe7d09b39be0a2fadc994/implicit_mass_spring.py#L156)

    **计算力**: [`compute_force()`](https://github.com/FantasyVR/taichi_course_final_project/blob/304a32dfa686862adcb54f737ed6970e21fe8d5b/implicit_mass_spring.py#L98)
     - 重力
     - 弹簧力
     - 约束力: 固定布料的两个顶点，使用一个刚度极大的弹簧来模拟。
     
    **计算力的导数**:[`compute_force_Jacobians`](https://github.com/FantasyVR/taichi_course_final_project/blob/304a32dfa686862adcb54f737ed6970e21fe8d5b/implicit_mass_spring.py#L120)
     - 弹簧力的导数
     - 约束力的导数
     
    **组装刚度矩阵**: [`assemble_K`](https://github.com/FantasyVR/taichi_course_final_project/blob/304a32dfa686862adcb54f737ed6970e21fe8d5b/implicit_mass_spring.py#L138)
     - 遍历每个弹簧，组建度矩阵
     
    **组装系统矩阵**：[here](https://github.com/FantasyVR/taichi_course_final_project/blob/304a32dfa686862adcb54f737ed6970e21fe8d5b/implicit_mass_spring.py#L162)
     - 系统矩阵<img src="https://user-images.githubusercontent.com/6712304/145008587-696452f3-497e-4b6e-985d-2f7f8720110a.png" width="100">
     
    **计算系统矩阵右侧b**: [here](https://github.com/FantasyVR/taichi_course_final_project/blob/304a32dfa686862adcb54f737ed6970e21fe8d5b/implicit_mass_spring.py#L169)
     - <img src="https://user-images.githubusercontent.com/6712304/145009103-ac8720e1-61ec-4dda-9121-820a62376316.png" width="150">

    **求解线性系统**: [here](https://github.com/FantasyVR/taichi_course_final_project/blob/304a32dfa686862adcb54f737ed6970e21fe8d5b/implicit_mass_spring.py#L171)
     - <img src="https://user-images.githubusercontent.com/6712304/145009271-67a7d412-eebd-41f8-9fbf-a22eb8f12bba.png" width="100">

    **更新速度和位置**: [`directUpdatePosVel`](https://github.com/FantasyVR/taichi_course_final_project/blob/8f79e0026237e75ec3abe7d09b39be0a2fadc994/implicit_mass_spring.py#L151)
     - <img src="https://user-images.githubusercontent.com/6712304/145009488-40d3a2d2-5d0c-454c-b654-235d94ae724d.png" width="200">
     
3. 布料更新 CG solver: [`update_cg(h)`](https://github.com/FantasyVR/taichi_course_final_project/blob/8f79e0026237e75ec3abe7d09b39be0a2fadc994/implicit_mass_spring.py#L249)

   在使用CG进行布料更新的时候，同样需要计算力和计算力的导数。但我们使用CG的时候，不需要显式的构建出刚度矩阵，只需要计算矩阵-向量乘就可以。具体算法请参考：[here](https://github.com/taichiCourse01/taichiCourse01/blob/main/material/09_implicit_integration.pdf) (P105-110)。

