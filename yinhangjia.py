# banker_sim.py
# 银行家算法动态分配演示（CLI交互版）
# 运行：python banker_sim.py

from dataclasses import dataclass
from typing import List, Tuple, Optional

def vec_le(a: List[int], b: List[int]) -> bool:
    return all(x <= y for x, y in zip(a, b))

def vec_add(a: List[int], b: List[int]) -> List[int]:
    return [x + y for x, y in zip(a, b)]

def vec_sub(a: List[int], b: List[int]) -> List[int]:
    return [x - y for x, y in zip(a, b)]

def fmt_vec(v: List[int]) -> str:
    return '[' + ' '.join(f'{x:>3d}' for x in v) + ']'

def fmt_mat(mat: List[List[int]]) -> str:
    return '\n'.join('  ' + fmt_vec(row) for row in mat)

@dataclass
class BankerSystem:
    n: int
    m: int
    available: List[int]
    max_need: List[List[int]]
    allocation: List[List[int]]

    def need(self) -> List[List[int]]:
        return [[self.max_need[i][j] - self.allocation[i][j] for j in range(self.m)] for i in range(self.n)]

    def safety_check(self, verbose: bool = True) -> Tuple[bool, List[int]]:
        need = self.need()
        work = self.available[:]
        finish = [False] * self.n
        seq: List[int] = []

        if verbose:
            print('\n安全性算法开始')
            print('Work0 =', fmt_vec(work))

        changed = True
        while changed:
            changed = False
            for i in range(self.n):
                if (not finish[i]) and vec_le(need[i], work):
                    if verbose:
                        print(f'  选中 P{i}: Need={fmt_vec(need[i])} <= Work={fmt_vec(work)}')
                    work = vec_add(work, self.allocation[i])
                    finish[i] = True
                    seq.append(i)
                    changed = True
                    if verbose:
                        print(f'    Work <- Work + Allocation(P{i}) = {fmt_vec(work)}')
        safe = all(finish)
        if verbose:
            if safe:
                print('安全：存在安全序列 =', seq)
            else:
                not_done = [i for i, f in enumerate(finish) if not f]
                print('不安全：无法继续满足的进程集合 =', not_done)
        return safe, seq

    def request(self, pid: int, req: List[int], verbose: bool = True) -> bool:
        if pid < 0 or pid >= self.n:
            raise ValueError('pid 越界')
        if len(req) != self.m:
            raise ValueError('请求向量维度不对')

        need = self.need()

        if verbose:
            print(f'\n事件：P{pid} 申请 Request = {fmt_vec(req)}')

        if not vec_le(req, need[pid]):
            if verbose:
                print('拒绝：Request > Need')
                print('Need =', fmt_vec(need[pid]))
            return False

        if not vec_le(req, self.available):
            if verbose:
                print('拒绝：Request > Available')
                print('Available =', fmt_vec(self.available))
            return False

        # 试分配
        avail2 = vec_sub(self.available, req)
        alloc2 = [row[:] for row in self.allocation]
        alloc2[pid] = vec_add(alloc2[pid], req)

        tmp = BankerSystem(self.n, self.m, avail2, [row[:] for row in self.max_need], alloc2)

        if verbose:
            print('试分配后：')
            print('  Available =', fmt_vec(tmp.available))
            print(f'  Allocation(P{pid}) =', fmt_vec(tmp.allocation[pid]))
            print(f'  Need(P{pid}) =', fmt_vec(tmp.need()[pid]))

        safe, seq = tmp.safety_check(verbose=verbose)

        if safe:
            self.available = avail2
            self.allocation = alloc2
            if verbose:
                print('批准：系统保持安全')
            return True
        else:
            if verbose:
                print('拒绝：试分配后系统不安全，已回滚')
            return False

    def release(self, pid: int, rel: List[int], verbose: bool = True) -> bool:
        if pid < 0 or pid >= self.n:
            raise ValueError('pid 越界')
        if len(rel) != self.m:
            raise ValueError('释放向量维度不对')

        if verbose:
            print(f'\n事件：P{pid} 释放 Release = {fmt_vec(rel)}')

        if not vec_le(rel, self.allocation[pid]):
            if verbose:
                print('拒绝：Release > Allocation')
                print('Allocation =', fmt_vec(self.allocation[pid]))
            return False

        self.allocation[pid] = vec_sub(self.allocation[pid], rel)
        self.available = vec_add(self.available, rel)

        if verbose:
            print('释放后：')
            print('  Available =', fmt_vec(self.available))
            print(f'  Allocation(P{pid}) =', fmt_vec(self.allocation[pid]))
            print(f'  Need(P{pid}) =', fmt_vec(self.need()[pid]))
        return True

    def show(self) -> None:
        need = self.need()
        print('\n系统状态')
        print('n =', self.n, 'm =', self.m)
        print('Available =', fmt_vec(self.available))
        print('\nMax:')
        print(fmt_mat(self.max_need))
        print('\nAllocation:')
        print(fmt_mat(self.allocation))
        print('\nNeed = Max - Allocation:')
        print(fmt_mat(need))

def read_ints(prompt: str, k: Optional[int] = None) -> List[int]:
    while True:
        s = input(prompt).strip()
        if not s:
            print('输入不能为空')
            continue
        parts = s.replace(',', ' ').split()
        try:
            nums = [int(x) for x in parts]
        except ValueError:
            print('请输入整数')
            continue
        if k is not None and len(nums) != k:
            print(f'需要 {k} 个整数')
            continue
        if any(x < 0 for x in nums):
            print('不允许负数')
            continue
        return nums

def main() -> None:
    print('银行家算法动态分配演示')
    n = int(input('输入进程数 n: ').strip())
    m = int(input('输入资源类数 m: ').strip())

    available = read_ints(f'输入 Available (共 {m} 个): ', k=m)

    max_need: List[List[int]] = []
    print(f'输入 Max 矩阵，共 {n} 行，每行 {m} 个整数')
    for i in range(n):
        row = read_ints(f'  Max P{i}: ', k=m)
        max_need.append(row)

    allocation: List[List[int]] = []
    print(f'输入 Allocation 矩阵，共 {n} 行，每行 {m} 个整数')
    for i in range(n):
        row = read_ints(f'  Allocation P{i}: ', k=m)
        allocation.append(row)

    # 基本合法性：Allocation <= Max
    for i in range(n):
        if not vec_le(allocation[i], max_need[i]):
            raise ValueError(f'初始化非法：P{i} 的 Allocation > Max')

    sys = BankerSystem(n, m, available, max_need, allocation)
    sys.show()

    print('\n命令：')
    print('  show                         显示矩阵')
    print('  safe                         运行安全性算法')
    print('  req  pid  r1 r2 ... rm        申请资源')
    print('  rel  pid  r1 r2 ... rm        释放资源')
    print('  quit                         退出')

    while True:
        cmdline = input('\n> ').strip()
        if not cmdline:
            continue
        parts = cmdline.split()
        op = parts[0].lower()

        try:
            if op == 'quit' or op == 'exit':
                break
            elif op == 'show':
                sys.show()
            elif op == 'safe':
                sys.safety_check(verbose=True)
            elif op == 'req':
                if len(parts) != 2 + m:
                    print(f'格式：req pid 后跟 {m} 个数')
                    continue
                pid = int(parts[1])
                req = [int(x) for x in parts[2:]]
                if any(x < 0 for x in req):
                    print('不允许负数')
                    continue
                sys.request(pid, req, verbose=True)
            elif op == 'rel':
                if len(parts) != 2 + m:
                    print(f'格式：rel pid 后跟 {m} 个数')
                    continue
                pid = int(parts[1])
                rel = [int(x) for x in parts[2:]]
                if any(x < 0 for x in rel):
                    print('不允许负数')
                    continue
                sys.release(pid, rel, verbose=True)
            else:
                print('未知命令')
        except Exception as e:
            print('错误：', e)

if __name__ == '__main__':
    main()
