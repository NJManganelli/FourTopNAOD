import re


class BranchSelection():
    def __init__(self, filename):
        comment = re.compile(r"#.*")
        ops = []
        for line in open(filename, 'r'):
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            line = re.sub(comment, "", line)
            while line[-1] == "\\":
                line = line[:-1] + " " + file.next().strip()
                line = re.sub(comment, "", line)
            try:
                (op, sel) = line.split()
                if op == "keep":
                    ops.append((sel, 1))
                elif op == "drop":
                    ops.append((sel, 0))
                elif op == "keepmatch":
                    ops.append((re.compile("(:?%s)$" % sel), 1))
                elif op == "dropmatch":
                    ops.append((re.compile("(:?%s)$" % sel), 0))
                else:
                    print("Error in file %s, line '%s': "% (filename, line)
                        + ": it's not (keep|keepmatch|drop|dropmatch) "
                        + "<branch_pattern>"
                    )
            except ValueError as e:
                print("Error in file %s, line '%s': " % (filename, line)
                    + "it's not (keep|keepmatch|drop|dropmatch) "
                    + "<branch_pattern>"
                )
        self._ops = ops

    def selectBranches(self, rdf_node):
        rdf_columns = [str(name) for name in rdf_node.GetColumnNames()]
        select_columns = []
        for bre, stat in self._ops:
            if type(bre) == re.Pattern:
                for n in rdf_columns:
                    if re.match(bre, n) and stat == 1:
                        #keepmatch
                        select_columns.append(n)
                    elif re.match(bre, n) and stat == 0:
                        select_columns = [brnch for brnch in select_columns if not re.match(bre, n)]
                        pass
            else:
                if stat == 1:
                    #keep
                    if bre == '*':
                        select_columns = [brnch for brnch in rdf_columns]
                    elif bre in rdf_columns:
                        select_columns.append(bre)
                else:
                    #drop
                    if bre == '*':
                        select_columns = []
                    else:
                        try:
                            select_columns.pop(select_columns.index(bre))
                        except Exception:
                            pass
        return select_columns
