import io
import sys
from typing import TextIO, Generator
from classes import Person, Student, Teacher, AssistantStudent, Req
from json import loads
from collections import namedtuple
from functools import partial
type = namedtuple('type', 'req_type field value returned')


def str_to_set(inp: str) -> set:
    inp = inp.strip('{}').split()
    for i in range(len(inp)):
        inp[i] = inp[i].strip('",')
    return set(inp)


def get_type(request: list, return_type=''):
    if not request:
        return type(Req.all, None, None, return_type)
    if 'is' in request:
        if 'set' in request:
            return type(Req.exist_field, request[0], None, return_type)
        if isinstance(request[2], list):
            return type(Req.field_value, request[0], get_type([request[2][0], request[2][1], request[2][2]], request[2][3]), return_type)
        return type(Req.field_value, request[0], request[2], return_type)
    if 'in' in request:
        if isinstance(request[2], list):
            return type(Req.field_collection, request[0], get_type([request[2][0], request[2][1], request[2][2]], request[2][3]), return_type)
        return type(Req.field_collection, request[0], request[2], return_type)
    if isinstance(request[2], list):
        return type(Req.field_contain, request[0], get_type([request[2][0], request[2][1], request[2][2]], request[2][3]), return_type)
    return type(Req.field_contain, request[0], request[2], return_type)


def reguest_handle(json_dict: dict, type_request: namedtuple) -> bool:
    if type_request.req_type == Req.all:
        return True
    elif type_request.field in json_dict:
        if type_request.req_type == Req.exist_field:
            return True
        elif type_request.req_type == Req.field_value:
            return str(json_dict[type_request.field]) == type_request.value
        elif type_request.req_type == Req.field_collection:
            collection = str_to_set(type_request.value)
            return json_dict[type_request.field] in collection
        elif type_request.req_type == Req.field_contain:
            if isinstance(json_dict[type_request.field], list):
                flag = False
                for el in json_dict[type_request.field]:
                    if type_request.value == str(el):
                        flag = True
                        break
                return flag


def gen_req(type_request: list, db_name: str) -> Generator:
    """
    это как handle только вернёт json_dict если ок и ещё это генератор
    """
    with open(db_name, "r", encoding="utf-8") as db:
        for line in db:
            json_dict = loads(line)
            if type_request.req_type == Req.all:
                yield json_dict
            elif type_request.field in json_dict:
                if type_request.req_type == Req.exist_field:
                    yield json_dict
                elif type_request.req_type == Req.field_value:
                    if str(json_dict[type_request.field]) == type_request.value:
                        yield json_dict
                elif type_request.req_type == Req.field_collection:
                    collection = str_to_set(type_request.value)
                    if json_dict[type_request.field] in collection:
                        yield json_dict
                elif type_request.req_type == Req.field_contain:
                    if isinstance(json_dict[type_request.field], list):
                        flag = False
                        for el in json_dict[type_request.field]:
                            if type_request.value == str(el):
                                flag = True
                                break
                        if flag:
                            yield json_dict

# type_ return только к generator


def decide_req(line: dict, req: tuple, type_return: str, db_name: str) -> bool:
    if not (isinstance(req.value, tuple)):
        return reguest_handle(line, req)
    curr_req = req.value
    generator = gen_req(curr_req, db_name)
    for el in generator:
        new_request = req
        new_request.value = el[type_return]
        if reguest_handle(line, el[type_return]):
            return True
    return False


def sub_generaror(type_requests: list, line: dict):
    logic_line = type_requests[:]
    for i in range(len(logic_line)):
        if isinstance(logic_line[i], tuple):
            if isinstance(logic_line[i].value, tuple):
                logic_line[i] = str(decide_req(
                    line, logic_line[i], logic_line[i].returned, db_name))
            else:
                logic_line[i] = str(reguest_handle(line, logic_line[i]))
                # logic_line: (,true,or,false,and,(,true,...),)
    if eval(' '.join(logic_line)):
        return line
    return None


def get_generator(type_requests: list, db_name: str) -> Generator:
    # db_name gener or str
    # type_requests: (,[re],or,[re],and,(,[re],...),)
    # request_handle вернёт true/false для строки и принимает json строку
    if isinstance(db_name, str):
        with open(db_name, "r", encoding="utf-8") as db:
            for line in db:
                res = sub_generaror(type_requests, loads(line))
                if res != None:
                    yield res
    else:
        for line in db_name:
            res = sub_generaror(type_requests, line)
            if res != None:
                yield res


def parse_input(inp: str) -> list:
    res = []
    word = ''
    i = 0
    while i < len(inp) and inp[i] != '\n':
        if inp[i] == '(' or inp[i] == ')' or inp[i] == '.':
            if word:
                res.append(word)
            word = ''
            res.append(inp[i])
            i += 1
            continue
        if inp[i] == ' ':
            if word:
                res.append(word)
            word = ''
            i += 1
            continue
        if inp[i] == '"':
            if word:
                res.append(word)
            word = ''
            i += 1
            while i < len(inp) and inp[i] != '"':
                word += inp[i]
                i += 1
            res.append(word)
            word = ''
            i += 1
            continue
        if inp[i] == '{':
            if word:
                res.append(word)
            word = ''
            while i < len(inp) and inp[i] != '}':
                word += inp[i]
                i += 1
            word += inp[i]
            res.append(word)
            word = ''
            i += 1
            continue
        word += inp[i]
        i += 1
    if word:
        res.append(word)
    return res


def parse_to_request(inp: list, from_reg: list, as_reg: list) -> list:
    if 'from' in inp:
        ind = inp.index('from')
        from_reg.append(inp[ind+1])
        inp.pop(ind+1)
        inp.pop(ind)
    if 'as' in inp:
        ind = inp.index('as')
        as_reg.append(inp[ind+1])
        inp.pop(ind+1)
        inp.pop(ind)
    while (True):
        if 'get' in inp:
            inp.remove('get')
        elif 'records' in inp:
            inp.remove('records')
        elif 'where' in inp:
            inp.remove('where')
        else:
            break
    while (True):
        if '.' in inp:
            summ = -1
            ind = inp.index('.')
            ind_end = ind+1
            repl = [inp[ind_end]]
            ind -= 2  # ).gr
            while summ:
                if inp[ind] == '(':
                    summ += 1
                elif inp[ind] == ')':
                    summ -= 1
                else:
                    repl.append(inp[ind])
                ind -= 1
            inp[ind+1] = repl[::-1]
            inp = inp[:ind+2]+inp[ind_end+2:]
        else:
            break
    res = []
    i = 0
    while i < len(inp):
        if inp[i] == '(' or inp[i] == ')' or inp[i] == 'and' or inp[i] == 'or':
            res.append(inp[i])
            i += 1
            continue
        res.append(get_type([inp[i], inp[i+1], inp[i+2]]))
        i += 3
    return res if res else [get_type([])]


assoc = dict()  # 'ddd': generator


def solution(requests: TextIO, db_name: str, output: TextIO) -> None:
    for request in requests:
        list_requests = parse_input(request)
        from_reg, as_reg = [], []
        list_requests = parse_to_request(
            list_requests, from_reg, as_reg)  # 3-> []
        # вход (,[re[gen?]],or,[re],and,(,[re],...),)
        source = db_name
        if from_reg:
            source = assoc[from_reg[0]][0]
            source = source(assoc[from_reg[0]][1], assoc[from_reg[0]][2])
        if as_reg:
            assoc[as_reg[0]] = [get_generator, list_requests, source]
            continue
        generator = get_generator(list_requests, source)
        for el in generator:
            human = None
            if "students" in el and "student_id" in el:
                human = AssistantStudent(el)
            elif "students" in el:
                human = Teacher(el)
            else:  # student_id
                human = Student(el)
            print(human.__str__(), file=output)


if __name__ == '__main__':
    print("$ ", end="")
    for line in sys.stdin:
        solution(io.StringIO(line.strip()), "db.txt", sys.stdout)
        print("$ ", end="")
