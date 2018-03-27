import time
import random

class Bot:

    def __init__(self):
    # TBD
        self.next_move = None
        self.next_move_cur = None
        self.start_time = 0
        self.time_limit = 15
        self.cur_depth = 3
        self.min_depth = 10
        self.infinity = 1000000000000000
        self.trans_table = {}
        self.grid_dict = {}
        self.comb_x = ((0,1,2,3),(0,1,2,3),(0,1,2,3),(0,1,2,3),(0,1,1,2),(0,1,1,2),(1,2,2,3),(1,2,2,3),(0,0,0,0),(1,1,1,1),(2,2,2,2),(3,3,3,3))
        self.comb_y = ((0,0,0,0),(1,1,1,1),(2,2,2,2),(3,3,3,3),(1,0,2,1),(2,1,3,2),(1,0,2,1),(2,1,3,2),(0,1,2,3),(0,1,2,3),(0,1,2,3),(0,1,2,3))
        self.draw_mapo = (6, 4, 4, 6, 4, 3, 3, 4, 4, 3, 3, 4, 6, 4, 4, 6)
        self.weight_mapo = (1, 2, 2, 1, 2, 3, 3, 2, 2, 3, 3, 2, 1, 2, 2, 1)
        self.board_view = [[0 for i in range(16)] for j in range(16)]
        self.block_view = [[0 for i in range(4)] for j in range(4)]
        self.bs_block = [[0 for i in range(4)] for j in range(4)]
        # optimize change_factor 
        change_factor = 10
        self.comb_pts = (0, 0, change_factor, 10 * change_factor, 50 * change_factor)

    def blockStatus(self):
        for ai in xrange(12):
            ch = self.bs_block[self.comb_x[ai][0]][self.comb_y[ai][0]] 
            if ch == 0 or ch == 2:
                break
            if ch == self.bs_block[self.comb_x[ai][1]][self.comb_y[ai][1]] == self.bs_block[self.comb_x[ai][2]][self.comb_y[ai][2]] == self.bs_block[self.comb_x[ai][3]][self.comb_y[ai][3]]:
                return ch

        for i in xrange(4):
            for j in xrange(4):
                if self.bs_block[i][j] == 0:
                    return 0

        return 2

    def boardStatus(self):
        for ai in xrange(12):
            ch = self.block_view[self.comb_x[ai][0]][self.comb_y[ai][0]] 
            if ch == 0 or ch == 2:
                break
            if ch == self.block_view[self.comb_x[ai][1]][self.comb_y[ai][1]] == self.block_view[self.comb_x[ai][2]][self.comb_y[ai][2]] == self.block_view[self.comb_x[ai][3]][self.comb_y[ai][3]]:
                return ch

        for i in xrange(4):
            for j in xrange(4):
                if self.block_view[i][j] == 0:
                    return 0

        return 2

    def allPossibleMoves(self, old_move):
        return_all_flag = False
        corr_x, corr_y = old_move[0]%4, old_move[1]%4
        if self.block_view[corr_x][corr_y] != 0:
            return_all_flag = True
        if return_all_flag:
            ret = []
            for i in xrange(4):
                for j in xrange(4):
                    if self.block_view[i][j] == 0:
                        row_off, col_off = 4*i, 4*j
                        for x in xrange(4):
                            for y in xrange(4):
                                if self.board_view[row_off + x][col_off + y] == 0:
                                    ret.append((row_off + x, col_off + y))
            return ret
        else:
            ret = []
            row_off, col_off = corr_x * 4, corr_y * 4
            for i in xrange(4):
                for j in xrange(4):
                    if self.board_view[row_off + i][col_off + j] == 0:
                        ret.append((row_off + i, col_off + j))
            return ret

    def terminalState(self):
        temp_stat = self.boardStatus()
        if temp_stat == 0:
            return False, None
        elif temp_stat == 1:
            return True, 1000000
        elif temp_stat == -1:
            return True, -1000000
        else:
            ret = 0
            count = 0
            for i in xrange(4):
                for j in xrange(4):
                    if self.block_view[i][j] in (1,-1):
                        ret += self.draw_mapo[count] * (self.block_view[i][j])
                        count += 1
            mult = 1
            if ret < 0:
                mult = -1
            return True, mult * (100000 + 10 * ret)

    def heuristicCalculatorBlock(self):
        temp_hash = hash(repr(self.bs_block))
        if temp_hash in self.grid_dict:
            return self.grid_dict[temp_hash]

        ans = 0
        #init
        count = 0
        for i in xrange(4):
            for j in xrange(4):
                if self.bs_block[i][j] == 1:
                    ans += self.weight_mapo[count]
                elif self.bs_block[i][j] == -1:
                    ans -= self.weight_mapo[count]
                count += 1

        #second part
        oneval, zeroval = 0, 0
        for comb in xrange(12):
            for i in xrange(4):
                val = self.bs_block[self.comb_x[comb][i]][self.comb_y[comb][i]]
                if val == 1:
                    oneval += 1
                elif val == -1:
                    zeroval += 1
            if oneval == 0:
                ans -= self.comb_pts[zeroval]
            else:
                ans += self.comb_pts[oneval]
            oneval, zeroval = 0, 0

        self.grid_dict[temp_hash] = ans
        return ans
         

    def heuristicCalculatorBoard(self):
        temp_hash = hash(repr(self.block_view))
        if temp_hash in self.grid_dict:
            return self.grid_dict[temp_hash]

        ans = 0
        #init
        count = 0
        for i in xrange(4):
            for j in xrange(4):
                if self.block_view[i][j] == 1:
                    ans += self.weight_mapo[count]
                elif self.block_view[i][j] == -1:
                    ans -= self.weight_mapo[count]
                count += 1

        #second part
        oneval, drawval, zeroval = 0, 0, 0
        for comb in xrange(12):
            for i in xrange(4):
                val = self.block_view[self.comb_x[comb][i]][self.comb_y[comb][i]]
                if val == 1:
                    oneval += 1
                elif val == -1:
                    zeroval += 1
                elif val == 2:
                    drawval += 1
            if drawval == 0:
                if oneval == 0:
                    ans -= self.comb_pts[zeroval]
                else:
                    ans += self.comb_pts[oneval]
            oneval, drawval, zeroval = 0, 0, 0

        self.grid_dict[temp_hash] = ans
        return ans

    def heuristicCalculatorTotal(self):
        ans = 0
        for i in xrange(4):
            for j in xrange(4):
                for k in xrange(4):
                    for l in xrange(4):
                        self.bs_block[k][l] = self.board_view[4*i + k][4*j + l]
                ans += self.heuristicCalculatorBlock()
        ans += self.heuristicCalculatorBoard() * 100
        return ans


    def minimax(self, alpha, beta, cur_flag, old_move, cur_depth, bonus_flag):
        if time.time() - self.start_time > self.time_limit:
            raise ValueError

        board_hash = hash(str(self.board_view))
        if cur_depth != self.cur_depth and board_hash in self.trans_table:
            temp_val = self.trans_table[board_hash]
            if temp_val[2] >= cur_depth:
                if temp_val[0] >= beta:
                    return temp_val[0]
                if temp_val[1] <= alpha:
                    return temp_val[1]
                alpha = max(alpha, temp_val[0])
                beta = min(beta, temp_val[1])

        self.min_depth = min(self.min_depth, cur_depth)

        final_state_stat, final_state_val = self.terminalState()

        if final_state_stat == True:
            if final_state_val != 0:
                return final_state_val
            else:
                if cur_flag:
                    return alpha
                else:
                    return beta

        ret = None

        if cur_depth == 1:
            ret = self.heuristicCalculatorTotal()

        elif cur_flag:

            cells = self.allPossibleMoves(old_move)
            random.shuffle(cells)
            ret = -self.infinity
            a = alpha
            limit = len(cells)

            for i in xrange(limit):
                if time.time() - self.start_time > self.time_limit:
                    raise ValueError

                if ret >= beta:
                    break

                move = cells[i]
                self.board_view[move[0]][move[1]] = 1
                tempi, tempj = (move[0]//4)*4, 4*(move[1]//4)
                for i in range(4):
                    for j in range(4):
                        self.bs_block[i][j] = self.board_view[tempi + i][tempj + j]
                bonus_temp = self.block_view[move[0]//4][move[1]//4] = self.blockStatus()

                val1, val2 = False, True
                if bonus_temp == 1 and bonus_flag:
                    val1, val2 = True, False

                tempRet = self.minimax(a, beta, val1, move, cur_depth - 1, val2)
                if cur_depth == self.cur_depth and tempRet > ret:
                    self.next_move_cur = move
                ret = max(ret, tempRet)
                a = max(a, ret)

                self.board_view[move[0]][move[1]] = 0
                self.block_view[move[0]//4][move[1]//4] = 0

        else:

            cells = self.allPossibleMoves(old_move)
            random.shuffle(cells)
            ret = self.infinity
            limit = len(cells)
            b = beta

            for i in xrange(limit):
                if time.time() - self.start_time > self.time_limit:
                    raise ValueError

                if ret <= alpha:
                    break

                move = cells[i]
                self.board_view[move[0]][move[1]] = -1

                tempi, tempj = (move[0]//4)*4, 4*(move[1]//4)
                for i in range(4):
                    for j in range(4):
                        self.bs_block[i][j] = self.board_view[tempi + i][tempj + j]
                bonus_temp = self.block_view[move[0]//4][move[1]//4] = self.blockStatus() 

                val1, val2 = True, True
                if bonus_temp == -1 and bonus_flag:
                    val1, val2 = False, False

                tempRet = self.minimax(alpha, b, val1, move, cur_depth - 1, val2)
                ret = min(ret, tempRet)
                b = min(b, ret)

                self.board_view[move[0]][move[1]] = 0
                self.block_view[move[0]//4][move[1]//4] = 0

        if ret <= alpha:
            self.trans_table[board_hash] = (-self.infinity, ret, cur_depth)
        if ret > alpha and ret < beta:
            self.trans_table[board_hash] = (ret, ret, cur_depth)
        if ret >= beta:
            self.trans_table[board_hash] = (-self.infinity, ret, cur_depth)
        return ret


    def move(self, board, old_move, flag):

        self.start_time = time.time()
        self.cur_depth = 3

        # Create board.
        for i in xrange(0,16):
            for j in xrange(0,16):
                if board.board_status[i][j] == flag:
                    self.board_view[i][j] = 1
                elif board.board_status[i][j] == '-':
                    self.board_view[i][j] = 0
                else:
                    self.board_view[i][j] = -1

        # Create blocks.
        for i in xrange(4):
            for j in xrange(4):
                if board.block_status[i][j] == flag:
                    self.block_view[i][j] = 1
                elif board.block_status[i][j] == '-':
                    self.block_view[i][j] = 0
                elif board.block_status[i][j] == 'd':
                    self.block_view[i][j] = 2
                else:
                    self.block_view[i][j] = -1

        if old_move == (-1,-1):
            print "here"
            return (7,7)
        bonus_flag = not (self.board_view[old_move[0]][old_move[1]] == 1)
        cells = self.allPossibleMoves(old_move)
        self.next_move = cells[0]

        try:
            while True:

                if time.time() - self.start_time > self.time_limit:
                    raise ValueError

                self.min_depth = self.cur_depth + 1

                self.minimax(-self.infinity, self.infinity, True, old_move, self.cur_depth, bonus_flag)

                if self.next_move_cur != None:
                    self.next_move = self.next_move_cur
                # print self.cur_depth
                # print self.next_move

                if self.min_depth > 1:
                    raise ValueError

                self.cur_depth += 1

        except ValueError:
            # print self.next_move
            return self.next_move 
