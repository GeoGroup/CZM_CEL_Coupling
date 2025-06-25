import re

with open(r'slide.inp', 'r') as file:
    inp_content = file.readlines()

nodes = []
elements = []
elsets = {}
current_elset_name = ""
in_node_section = False
in_element_section = False
in_elset_section = False
generate_next_line = False  # Flag to indicate the next line should be processed for 'generate'
start_node = 0
node_id = 0
end_node = 0
end_part = 0

for i, line in enumerate(inp_content):
    line = line.strip()
    if line.startswith('*End Part'):
        end_part = i
        break
    elif line.startswith('*Node'):
        start_node = i
        in_node_section = True
        in_element_section = False
        in_elset_section = False
    elif line.startswith('*Element'):
        in_node_section = False
        in_element_section = True
        in_elset_section = False
    elif line.startswith('*Elset'):
        parts = line.split(',')
        elset_name = parts[1].split('=')[1].strip()
        elsets[elset_name] = []
        current_elset_name = elset_name
        in_node_section = False
        in_element_section = False
        in_elset_section = True
        if 'generate' in line:
            generate_next_line = True  # Set flag to true to process the next line for 'generate'
    elif generate_next_line:
        start, end, step = [int(x.strip()) for x in line.split(',')]
        elsets[current_elset_name].extend(list(range(start, end + 1, step)))
        in_elset_section = False  # Reset section flags
        generate_next_line = False  # Reset the flag
    elif line.startswith('*'):
        in_node_section = False
        in_element_section = False
        in_elset_section = False
    else:
        if in_node_section:
            nodes.append(line)
        elif in_element_section:
            elements.append(line)
        elif in_elset_section:
            elsets[current_elset_name].extend([int(x.strip()) for x in line.split(',')])

# 提取节点和单元的详细信息
node_dict = {}
element_dict = {}
precohel_dict = {}

# 正则表达式以匹配两种格式
# 第一种格式: 数字可能包含e或E表示的科学计数法
# 第二种格式: 简单的浮点数或整数，不包含科学计数法

node_pattern1 = re.compile(
    r'(\d+)\s*,\s*([-+]?\d*\.?\d*[eE][-+]?\d+)\s*,\s*([-+]?\d*\.?\d*[eE][-+]?\d+)\s*,\s*([-+]?\d*\.?\d*'
    r')'
)

node_pattern2 = re.compile(
    r'(\d+)\s*,\s*([-+]?\d*\.?\d*)\s*,\s*([-+]?\d*\.?\d*)\s*,\s*([-+]?\d*\.?\d*)'
)
element_pattern_c3d8 = re.compile(r'(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,'
                                  r'\s*(\d+)\s*,\s*(\d+)')
element_pattern_c3d6 = re.compile(r'(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)')
element_pattern_c3d5 = re.compile(r'(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)')
element_pattern_c3d4 = re.compile(r'(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)')

# 解析节点
for node in nodes:
    match = node_pattern2.match(node)
    if match:
        node_id = int(match.group(1))
        coordinates = (float(match.group(2)), float(match.group(3)), float(match.group(4)))
        node_dict[node_id] = coordinates
end_node = start_node + node_id
# 解析单元
for element in elements:
    match_c3d8 = element_pattern_c3d8.match(element)
    if match_c3d8:
        element_id = int(match_c3d8.group(1))
        node_ids = list(int(match_c3d8.group(i)) for i in range(2, 10))
        element_dict[element_id] = node_ids
    else:
        # 匹配C3D6单元
        match_c3d6 = element_pattern_c3d6.match(element)
        if match_c3d6:
            element_id = int(match_c3d6.group(1))
            node_ids = list(int(match_c3d6.group(i)) for i in range(2, 8))
            element_dict[element_id] = node_ids
        else:
            # 匹配C3D5单元
            match_c3d5 = element_pattern_c3d5.match(element)
            if match_c3d5:
                element_id = int(match_c3d5.group(1))
                node_ids = list(int(match_c3d5.group(i)) for i in range(2, 7))
                element_dict[element_id] = node_ids
            else:
                # 匹配C3D4单元
                match_c3d4 = element_pattern_c3d4.match(element)
                if match_c3d4:
                    element_id = int(match_c3d4.group(1))
                    node_ids = list(int(match_c3d4.group(i)) for i in range(2, 6))
                    element_dict[element_id] = node_ids

# 解析分组
coh_set = set(elsets['slide'])
coh_elements = {}
all_elements_set = set(element_dict.keys())
not_coh_elements = all_elements_set - coh_set

for element in coh_set:
    coh_elements[element] = element_dict[element]

print(f"读取到 {len(node_dict)} 个节点")
print(f"读取到 {len(element_dict)} 个单元")

new_elements = {}
new_nodes = {}
node_new_old = {}
new_node_id = 0

# 拆面
for element_id, element_nodes in element_dict.items():
    new_element_nodes = []
    for node_index, node in enumerate(element_nodes):
        new_node_id = new_node_id + 1
        node_new_old[new_node_id] = node
        new_element_nodes.append(new_node_id)
        new_nodes[new_node_id] = node_dict[node]
    new_elements[element_id] = new_element_nodes

print(f"读取到 {len(new_nodes)} 个节点")
print(f"读取到 {len(new_elements)} 个单元")


def get_faces(new_elements1, element_dict1):
    faces = {}
    face_id = 1
    face_list_new = []
    face_list_old = []
    for key, value in new_elements.items():
        node_new = new_elements1[key]
        node_old = element_dict1[key]
        if len(value) == 8:
            face_list_new = [[node_new[3], node_new[2], node_new[1], node_new[0]],
                             [node_new[4], node_new[5], node_new[6], node_new[7]],
                             [node_new[0], node_new[1], node_new[5], node_new[4]],
                             [node_new[1], node_new[2], node_new[6], node_new[5]],
                             [node_new[2], node_new[3], node_new[7], node_new[6]],
                             [node_new[3], node_new[0], node_new[4], node_new[7]]]
            face_list_old = [[node_old[3], node_old[2], node_old[1], node_old[0]],
                             [node_old[4], node_old[5], node_old[6], node_old[7]],
                             [node_old[0], node_old[1], node_old[5], node_old[4]],
                             [node_old[1], node_old[2], node_old[6], node_old[5]],
                             [node_old[2], node_old[3], node_old[7], node_old[6]],
                             [node_old[3], node_old[0], node_old[4], node_old[7]]]
        if len(value) == 6:
            face_list_new = [[node_new[2], node_new[1], node_new[0]],
                             [node_new[3], node_new[4], node_new[5]],
                             [node_new[0], node_new[1], node_new[4], node_new[3]],
                             [node_new[1], node_new[2], node_new[5], node_new[4]],
                             [node_new[2], node_new[0], node_new[3], node_new[5]]]
            face_list_old = [[node_old[2], node_old[1], node_old[0]],
                             [node_old[3], node_old[4], node_old[5]],
                             [node_old[0], node_old[1], node_old[4], node_old[3]],
                             [node_old[1], node_old[2], node_old[5], node_old[4]],
                             [node_old[2], node_old[0], node_old[3], node_old[5]]]
        if len(value) == 5:
            face_list_new = [[node_new[3], node_new[2], node_new[1], node_new[0]],
                             [node_new[0], node_new[1], node_new[4]],
                             [node_new[1], node_new[2], node_new[4]],
                             [node_new[2], node_new[3], node_new[4]],
                             [node_new[3], node_new[0], node_new[4]]]
            face_list_old = [[node_old[3], node_old[2], node_old[1], node_old[0]],
                             [node_old[0], node_old[1], node_old[4]],
                             [node_old[1], node_old[2], node_old[4]],
                             [node_old[2], node_old[3], node_old[4]],
                             [node_old[3], node_old[0], node_old[4]]]
        if len(value) == 4:
            face_list_new = [[node_new[2], node_new[1], node_new[0]],
                             [node_new[0], node_new[1], node_new[3]],
                             [node_new[1], node_new[2], node_new[3]],
                             [node_new[2], node_new[0], node_new[3]]]
            face_list_old = [[node_old[2], node_old[1], node_old[0]],
                             [node_old[0], node_old[1], node_old[3]],
                             [node_old[1], node_old[2], node_old[3]],
                             [node_old[2], node_old[0], node_old[3]]]
        face_str_list = []
        face_list_old_copy = [iface.copy() for iface in face_list_old]  # 创建 face_list_old 的深层副本
        for iface in face_list_old_copy:
            iface.sort()
            iface = [str(i) for i in iface]
            iface_str = '_'.join(iface)
            face_str_list.append(iface_str)
        for i in range(len(face_list_new)):
            faces[face_id] = {'ele_id': key,
                              'new_id': face_list_new[i],
                              'old_id': face_list_old[i],
                              'str': face_str_list[i],
                              'count': len(face_list_new)}
            face_id = face_id + 1
    return faces


faces = get_faces(new_elements, element_dict)

unique_faces = {}
for i in faces.keys():
    face_str = faces[i]['str']
    if unique_faces.get(face_str) is None:
        unique_faces[face_str] = [i]
    else:
        unique_faces[face_str].append(i)
unique_faces1 = {}
unique_faces2 = {}
for str_index, face_indexes in unique_faces.items():
    if len(face_indexes) == 2:
        if all(faces[face_index]['ele_id'] in coh_set for face_index in face_indexes):
            unique_faces1[str_index] = face_indexes
        elif sum(faces[face_index]['ele_id'] in coh_set for face_index in face_indexes) == 1:
            unique_faces2[str_index] = face_indexes
unique_faces3 = {}
unique_faces3.update(unique_faces1)
unique_faces3.update(unique_faces2)

coh_faces = {}
# 形成set中coh
coh_id = 1
cohin_faces = {}
cohnodes_set = set()

node_to_new_nodes = {}
for new_node, old_node in node_new_old.items():
    if old_node not in node_to_new_nodes:
        node_to_new_nodes[old_node] = list()
    node_to_new_nodes[old_node].append(new_node)

for str_index, face_index in unique_faces1.items():
    if len(face_index) == 2:
        face_couple = []
        face1 = faces[face_index[0]]['new_id']
        face2 = faces[face_index[1]]['new_id']
        face2_nodes_set = set(face2)
        face2_1 = []
        for idx in face1:
            old_node = node_new_old[idx]
            if old_node in node_to_new_nodes:
                for may_node in node_to_new_nodes[old_node]:
                    if may_node in face2_nodes_set:
                        face2_1.append(may_node)
        face_couple.extend(face1)
        face_couple.extend(face2_1)
        cohin_faces[coh_id] = face_couple
        coh_faces.update(cohin_faces)
        cohnodes_set.update(set(face_couple))
        coh_id += 1

# 缝合
new_new = {}
for newnodes in node_to_new_nodes.values():
    for node in newnodes:
        if node not in cohnodes_set:
            new_new[node] = newnodes[0]
    for node in newnodes[1:]:
        if node not in cohnodes_set:
            del new_nodes[node]
for index, nodes in new_elements.items():
    if index in not_coh_elements:
        for i, node in enumerate(nodes):
            if node in new_new.keys():
                new_elements[index][i] = new_new[node]

print(f"读取到 {len(new_nodes)} 个节点")
print(f"读取到 {len(new_elements)} 个单元")

# 形成set外coh
faces1 = get_faces(new_elements, element_dict)
cohout_faces = {}
cohout_id = 1 + coh_id
for str_index, face_index in unique_faces2.items():
    if len(face_index) == 2:
        face_couple = []
        face1 = faces1[face_index[0]]['new_id']
        face2 = faces1[face_index[1]]['new_id']
        face2_nodes_set = set(face2)
        face2_1 = []
        for idx in face1:
            old_node = node_new_old[idx]
            if old_node in node_to_new_nodes:
                for may_node in node_to_new_nodes[old_node]:
                    if may_node in face2_nodes_set:
                        face2_1.append(may_node)
        face_couple.extend(face1)
        face_couple.extend(face2_1)
        cohout_faces[cohout_id] = face_couple
        cohout_id += 1
        coh_faces.update(cohout_faces)

# 生成inp文件内容
with open(r"slide-1.inp", "w") as file:
    # 写入节点部分
    content_to_write = inp_content[:start_node]
    file.writelines(content_to_write)
    file.write("*NODE\n")
    for node_id, coords in new_nodes.items():
        file.write(f"{node_id}, {coords[0]}, {coords[1]}, {coords[2]}\n")
    # 写入单元部分
    file.write("*ELEMENT, TYPE=C3D8\n")
    for element_id, element_nodes in new_elements.items():
        if len(element_nodes) == 8:
            file.write(f"{element_id}, {', '.join(map(str, element_nodes))}\n")
    file.write("*ELEMENT, TYPE=C3D4\n")
    for element_id, element_nodes in new_elements.items():
        if len(element_nodes) == 4:
            file.write(f"{element_id}, {', '.join(map(str, element_nodes))}\n")
    file.write("*ELEMENT, TYPE=C3D6\n")
    for element_id, element_nodes in new_elements.items():
        if len(element_nodes) == 6:
            file.write(f"{element_id}, {', '.join(map(str, element_nodes))}\n")
    file.write("*ELEMENT, TYPE=C3D5\n")
    for element_id, element_nodes in new_elements.items():
        if len(element_nodes) == 5:
            file.write(f"{element_id}, {', '.join(map(str, element_nodes))}\n")
    file.write("*ELEMENT, TYPE=COH3D6\n")
    for element_id, element_nodes in coh_faces.items():
        if len(element_nodes) == 6:
            file.write(f"{element_id + len(element_dict)}, {', '.join(map(str, element_nodes))}\n")
    file.write("*ELEMENT, TYPE=COH3D8\n")
    for element_id, element_nodes in coh_faces.items():
        if len(element_nodes) == 8:
            file.write(f"{element_id + len(element_dict)}, {', '.join(map(str, element_nodes))}\n")
    # 写入elsets部分，每行最多16个element
    for elset_name, elset_elements in elsets.items():
        file.write(f'*Elset, elset={elset_name}\n')
        for i in range(0, len(elset_elements), 16):
            file.write(', '.join(map(str, elset_elements[i:i + 16])) + '\n')
    file.write("*Elset, elset=cohin\n")
    for i in range(0, len(cohin_faces), 16):
        keys_slice = list(cohin_faces.keys())[i:i + 16]
        keys_str = ", ".join(map(lambda key: str(key + len(element_dict)), keys_slice))
        file.write(keys_str + "\n")
    file.write("*Elset, elset=cohout\n")
    for i in range(0, len(cohout_faces), 16):
        keys_slice = list(cohout_faces.keys())[i:i + 16]
        keys_str = ", ".join(map(lambda key: str(key + len(element_dict)), keys_slice))
        file.write(keys_str + "\n")
    # for i, line in enumerate(inp_content):
    #     line = line.strip()
    #     if line.startswith('** Section'):
    #         section_count += 1
    #         if section_count == 1:
    #             start_section = i
    #     if line.startswith('*End Part'):
    #         end_part = i
    #     if line.startswith('** ASSEMBLY'):
    #         start_as = i
    #     if line.startswith('*End Assembly'):
    #         end_as = i
    #     if line.startswith('** ASSEMBLY'):
    #         start_as = i
    #     if line.startswith('*End Assembly'):
    #         end_as = i
    content_to_write = inp_content[end_part:]
    file.writelines(content_to_write)


