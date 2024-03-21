import math
import gradio as gr
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np


# 定义一个表示个人的类
class person_p:
    def __init__(self, attributes, relationship) -> None:
        # 初始化个人属性
        self.attributes = attributes  # 个人的详细信息，如姓名、性别等
        self.seniors = []  # 存储年长者的列表
        self.peers = []  # 存储同辈的列表
        self.juniors = []  # 存储年幼者的列表
        self.age_level = 0  # 个人在家族树中的年龄层级

    # 更新个人属性的方法
    def update(self, update_data):
        # 遍历更新数据中的每一个项
        for key, value in update_data.items():
            # 如果键存在于属性中，并且值不为空，则更新属性
            if key in self.attributes and value != "":
                self.attributes[key] = value

# 定义一个表示家族的类
class family:
    def __init__(self) -> None:
        self.people = []  # 存储家族成员的列表
        self.ids = []  # 存储成员身份标识的列表

    # 添加一个新成员的方法
    def add(self, person, id_):
        self.people.append(person)  # 添加成员对象
        self.ids.append(id_)  # 添加成员的身份标识

    # 更新成员信息的方法
    def update(self, update_values, id_):
        # 遍历所有成员身份标识
        for index, id_t in enumerate(self.ids):
            # 如果找到匹配的身份标识
            if id_t == id_:
                # 更新该成员的信息
                self.people[index].update(update_values)
                return


fam = family()

# 定义一个清空所有输入字段的函数
def clear_all(
    identity,
    fn,
    ln,
    lnb,
    living,
    gen,
    birth_mon,
    birth_day,
    birth_year,
    relationship,
    relathipship_id,
    contect,
    bio,
):
    return ["", "", "", "", False, None, None, None, "", "", "", None, ""]


# 定义一个添加或更新家族成员的函数
def add_person(
    identity,
    fn,
    ln,
    lnb,
    living,
    gen,
    birth_mon,
    birth_day,
    birth_year,
    relationship,
    relationship_id,
    contact,
    bio,
):
    # 创建一个字典，用于存储更新的值
    update_values = {}
    update_values["identity"] = identity
    update_values["first_name"] = fn
    update_values["last_name"] = ln
    update_values["gender"] = gen
    update_values["last_name_birth"] = lnb
    update_values["living"] = living
    update_values["birth_month"] = birth_mon
    update_values["birth_day"] = birth_day
    update_values["birth_year"] = birth_year
    update_values["relationship"] = relationship
    update_values["relationship_id"] = relationship_id
    update_values["contact"] = contact
    update_values["bio"] = bio
    # 如果身份标识已存在于家族中，则更新该成员信息,否则添加一个新成员
    if identity in fam.ids:
        fam.update(update_values, identity)
    else:
        # 如果不存在，则创建一个新的 person_p 实例并添加到家族中
        fam.add(person_p(update_values, relationship_id), identity)
    # 获取成员在家族列表中的索引
    current_index = fam.ids.index(identity)
    # 如果不是Me
    if identity != "Me":
        # 若未在家族成员列表中报错并返回
        if relationship_id not in fam.ids:
            return "Please input an identity recorded!!!", go.Figure()
        # 获取关系成员的索引
        index = fam.ids.index(relationship_id)
        # 如果是Senior，将其添加到Senior列表中，同时age_level - 1
        if relationship == "Senior":
            fam.people[index].seniors.append(identity)
            fam.people[current_index].age_level = fam.people[index].age_level - 1
        # 如果是Peer，将其添加到Peer列表中，age_level不变
        elif relationship == "Peer":
            fam.people[index].peers.append(identity)
            fam.people[current_index].age_level = fam.people[index].age_level
        # 如果是juniors，将其添加到juniors列表中，age_level + 1
        else:
            fam.people[index].juniors.append(identity)
            fam.people[current_index].age_level = fam.people[index].age_level + 1
    else:
        # 其他情况，设置age_level为0
        fam.people[current_index].age_level = 0
    # 获取所有成员的年龄层级并排序，以便可视化表示时按年龄层级排列
    ages_levels = [per.age_level for per in fam.people]
    sort_index = np.argsort(np.array(ages_levels))
    fam.people = [fam.people[i] for i in sort_index]
    fam.ids = [fam.ids[i] for i in sort_index]
    # 初始化用于可视化的各种变量
    pos = {}  # 存储每个成员的位置
    # 当前成员的x、y坐标
    current_x = 0
    current_y = 0
    # 所有成员的x、y坐标列表
    xn = []
    yn = []
    annotations = []  # 标注列表
    color_ops = []  # 颜色列表
    org_color = 55
    current_level = fam.people[0].age_level - 1  # 当前处理的年龄层级
    # 遍历所有家族成员，为可视化准备数据
    for index, person in enumerate(fam.people):
        # 如果当前成员的age_level与current_level不同，则重置x坐标，y坐标减小，并更新age_level
        if person.age_level != current_level:
            current_x = 0
            current_y -= 0.25
            current_level = person.age_level
        else:
            # 如果是同一层级的下一个成员，则x坐标增加，表示在同一层级中排列
            current_x += 0.25
        # 根据age_level调整颜色，并存储位置信息
        color_ops.append("rgb(" + str(50 + person.age_level * 5) + ",50,50)")
        pos[person.attributes["identity"]] = (current_x, current_y)
        xn.append(current_x)
        yn.append(current_y)
        # 添加标注信息，包括坐标、字体样式、不显示指向箭头
        annotations.append(
            dict(
                text=person.attributes["identity"],
                # + ":\n"
                # + person.attributes["first_name"]
                # + "\n"
                # + person.attributes[
                #     "last_name"
                # ],  # or replace labels with a different list for the text within the circle
                x=current_x,
                y=current_y,
                xref="x1",
                yref="y1",
                font=dict(color="rgb(250,250,250)", size=15),
                showarrow=False,
            )
        )
    # 连接线的x、y坐标对
    xe = []
    ye = []
    # 遍历所有家族成员并绘制连接线
    for index, person in enumerate(fam.people):
        # 对于每个成员，添加其与所有senior、peer、junior的连接线
        current_id = person.attributes["identity"]
        for senior in person.seniors:
            xe.append([pos[current_id][0], pos[senior][0]])
            ye.append([pos[current_id][1], pos[senior][1]])
        for peer in person.peers:
            xe.append([pos[current_id][0], pos[peer][0]])
            ye.append([pos[current_id][1], pos[peer][1]])
        for junior in person.juniors:
            xe.append([pos[current_id][0], pos[junior][0]])
            ye.append([pos[current_id][1], pos[junior][1]])
    # 初始化一个空的绘图对象
    fig = go.Figure()

    # 添加所有连接线到绘图对象
    for zip_x, zip_y in zip(xe, ye):
        fig.add_trace(
            go.Scatter(
                x=zip_x,
                y=zip_y,
                mode="lines",
                line=dict(color="rgb(210,210,210)", width=1),
                hoverinfo="none",
            )
        )
    # 将每个家族成员表示为图中的一个标记（点），并设置标注
    for index, xn_ in enumerate(xn):
        fig.add_trace(
            go.Scatter(
                # x、y坐标
                x=[xn_],
                y=[yn[index]],
                mode="markers",
                name="bla",
                # 标记形状、大小、颜色
                marker=dict(
                    symbol="circle-dot",
                    size=50,
                    color=color_ops[index],  #'#DB4551',
                    line=dict(color="rgb(50,50,50)", width=1),
                ),
                hoverinfo="text", # 鼠标悬停显示文本信息
                opacity=0.8, # 标记透明度
            )
        )
    # 设置坐标轴的显示属性
    axis = dict(
        showline=False,  # hide axis line, grid, ticklabels and  title
        zeroline=False,
        showgrid=False,
        showticklabels=False,
    )
    # 更新图表的布局设置
    fig.update_layout(
        title="",   # 图表标题为空
        annotations=annotations, # 添加之前准备的所有标注
        font_size=12,
        showlegend=False,
        xaxis=axis,
        yaxis=axis,
        margin=dict(l=40, r=40, b=85, t=100),  # 设置图表边距
        hovermode="closest",  # 鼠标悬停模式设置为"最近的点"
        plot_bgcolor="rgb(248,248,248)",
    )
    # 再次更新图表布局，设置图表的宽度和高度为1000
    fig.update_layout(
        width=1000,
        height=1000,
    )
    return identity, fig

# 定义一个显示指定成员的信息的函数
def present_info(identity):
    # 如果指定的身份标识存在于家族中
    if identity in fam.ids:
        # 获取该成员的信息
        values = fam.people[fam.ids.index(identity)]
        # 返回成员的所有属性值
        return list(values.attributes.values())
    # 如果身份标识不存在，返回一个包含错误信息和空值的列表
    return [
        "This person's information is not recorded!!!",
        "",
        "",
        "",
        False,
        None,
        None,
        None,
        "",
        "",
        "",
        None,
        "",
    ]

# 使用Blocks API创建Gradio应用的界面
block = gr.Blocks().queue()
with block:
    with gr.Row(): # 标题行
        gr.Markdown("## A dynamic family tree.") 
    with gr.Column():  # 创建展示家族树的列
        gr.Label("Family tree:")
        tree = gr.Plot()
    with gr.Row():  # 创建包含个人信息输入字段的行和列
        with gr.Tab("Personal"):
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        identity = gr.Textbox("Identity: (e.g. Me, Father, Mother))")
                        show_info = gr.Button("Show info")
                    fn = gr.Textbox(label="Given names:")
                    ln = gr.Textbox(label="Surname now:")
                    lnb = gr.Textbox(label="Surname at birth:")
                    gen = gr.Radio(["Female", "Male", "Other"], label="Gender:")
                    with gr.Row():
                        gr.Label("Birth date:")
                        birth_mon = gr.Dropdown(
                            [
                                "Jan",
                                "Feb",
                                "Mar",
                                "Apr",
                                "May",
                                "Jun",
                                "Jul",
                                "Aug",
                                "Sept",
                                "Oct",
                                "Nov",
                                "Dec",
                            ],
                            label="",
                        )
                        birth_day = gr.Dropdown(
                            [str(i) for i in range(1, 32)], label=""
                        )
                        birth_year = gr.Textbox(label="")
                    living = gr.Checkbox(label="This person is living", value=False)
                    with gr.Row():
                        relationship = gr.Radio(
                            ["Senior", "Peer", "Junior"], label="Relationship to"
                        )
                        relationship_id = gr.Textbox(label="")
                    with gr.Row():
                        gr.Label("You can also add or change details later")
                        ok_button = gr.Button(value="OK")
                        cancel_button = gr.Button(value="Cancel")
        # 创建包含Contact的标签页
        with gr.Tab("Contact"):
            contact = gr.Textbox("Contact information is: ")
        # 创建包含biography的标签页
        with gr.Tab("Biography"):
            bio = gr.Textbox("My biography is: ")
    # 为cancel_button绑定清除功能
    cancel_button.click(
        clear_all,
        inputs=[
            identity,
            fn,
            ln,
            lnb,
            living,
            gen,
            birth_mon,
            birth_day,
            birth_year,
            relationship,
            relationship_id,
            contact,
            bio,
        ],
        outputs=[
            identity,
            fn,
            ln,
            lnb,
            living,
            gen,
            birth_mon,
            birth_day,
            birth_year,
            relationship,
            relationship_id,
            contact,
            bio,
        ],
    )
    # 为OK按钮绑定添加人物的功能
    ok_button.click(
        add_person,
        inputs=[
            identity,
            fn,
            ln,
            lnb,
            living,
            gen,
            birth_mon,
            birth_day,
            birth_year,
            relationship,
            relationship_id,
            contact,
            bio,
        ],
        outputs=[identity, tree],
    )
    # 为show_info按钮绑定显示选定家族成员信息的功能
    show_info.click(
        present_info,
        inputs=[identity],
        outputs=[
            identity,
            fn,
            ln,
            lnb,
            living,
            gen,
            birth_mon,
            birth_day,
            birth_year,
            relationship,
            relationship_id,
            contact,
            bio,
        ],
    )
# 启动Gradio应用
block.launch(server_name="0.0.0.0")
