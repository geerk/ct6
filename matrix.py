class matrix(object):
    def __init__(self,mat):
        if mat == 1:
            mat = [[r == c and 1 or 0 for r in range(4)] for c in range(4)]
        self.mat = mat
        self.row = len(mat)
        self.col = len(mat[0])
        self._matRes = []
        self.__s = ''
        
    def __str__(self):
        for i in range(self.row):
            self.__s += '\n'
            for j in range(self.col):
                self.__s += '%g\t' %(self.mat[i][j])
        return self.__s
    
    def __repr__(self):
        return repr(self.mat)
        
    def __eq__(self, y):
        return self.mat == y.mat
    
    def __mul__(self, other):
        if isinstance(other,int) or isinstance(other,float):
            for i in range(self.row):
                for j in range(self.col):
                    self.mat[i][j] *= other
            return matrix(self.mat)
                
        if self.col != other.row: return 'The number of columns of the first matrix must be equal to the number of rows of the second.'
        self._matRes = [[0 for r in range(other.col)] for c in range(self.row)]
        for i in range(self.row):
            for j in range(other.col):
                for k in range(other.row):
                    self._matRes[i][j] += self.mat[i][k] * other.mat[k][j]
        return matrix(self._matRes)
    
    def tolist(self):
        return self.mat
