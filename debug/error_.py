from utils.string_with_arrows import *

class Position:
    def __init__(self, idx, ln, col,fn,ftxt) -> None:
        self.idx = idx
        self.ln = ln
        self.col = col

        self.fn = fn
        self.ftxt = ftxt
    
    def advance(self, currentChar=None):
        self.idx+=1
        self.col+=1

        if currentChar == "\n":
            self.ln+=1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col,self.fn, self.ftxt)

class Error:
    def __init__(self, pos_start, pos_end,error_name, details) -> None:
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_str(self):
        result = f'{self.error_name}: {self.details}'
        result += f'\nFile {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += f'\n\n'+string_with_arrows(self.pos_start.ftxt,self.pos_start,self.pos_end)

        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details) -> None:
        super().__init__(pos_start, pos_end,'Illegal Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details='') -> None:
        super().__init__(pos_start, pos_end,'Invalid Syntax', details)

class RTError(Error):
	def __init__(self, pos_start, pos_end, details, context):
		super().__init__(pos_start, pos_end, 'Runtime Error', details)
		self.context = context

	def as_string(self):
		result  = self.generate_traceback()
		result += f'{self.error_name}: {self.details}'
		result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
		return result

	def generate_traceback(self):
		result = ''
		pos = self.pos_start
		ctx = self.context

		while ctx:
			if pos is not None:
				result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
			else:
				result = f'  In {ctx.display_name}:\n' + result
			pos = ctx.parent_entry_pos
			ctx = ctx.parent

		return 'Traceback (most recent call last):\n' + result