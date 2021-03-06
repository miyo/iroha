"""Iroha IR builder in Python"""

import sys

class IDesign(object):
    def __init__(self):
        self.modules = []
        self.resource_classes = []
        self.installResourceClasses()
        self.resourceParams = ResourceParams()

    def Write(self, writer):
        self.resourceParams.Write(writer)
        for m in self.modules:
            m.Write(writer)

    def installResourceClasses(self):
        self.resource_classes.append(IResourceClass("set"))
        self.resource_classes.append(IResourceClass("tr"))
        self.resource_classes.append(IResourceClass("add"))
        self.resource_classes.append(IResourceClass("gt"))
        self.resource_classes.append(IResourceClass("array"))
        self.resource_classes.append(IResourceClass("embedded"))

    def findResourceClassByName(self, name):
        for rc in self.resource_classes:
            if rc.name == name:
                return rc
        return None

class IModule(object):
    def __init__(self, design, name):
        design.modules.append(self)
        self.design = design
        self.name = name
        self.tables = []
        self.parent_module = None
        self.resource_params = ResourceParams()

    def Write(self, writer):
        writer.ofh.write("(MODULE " + self.name + "\n")
        writer.ofh.write(" ")
        self.resource_params.Write(writer)
        if self.parent_module:
            writer.ofh.write(" (PARENT " + self.parent_module.name + ")\n")
        for t in self.tables:
            t.Write(writer)
        writer.ofh.write(")\n")

class ITable(object):
    def __init__(self, mod):
        mod.tables.append(self)
        self.module = mod
        self.resources = []
        self.states = []
        self.registers = []
        self.id = -1
        self.initialSt = None

    def Write(self, writer):
        writer.ofh.write(" (TABLE " + str(self.id) + "\n")
        writer.ofh.write("  (REGISTERS\n")
        for reg in self.registers:
            reg.Write(writer)
        writer.ofh.write("  )\n")
        writer.ofh.write("  (RESOURCES\n")
        for res in self.resources:
            res.Write(writer)
        writer.ofh.write("  )\n")
        if self.initialSt:
            writer.ofh.write("  (INITIAL " + str(self.initialSt.id) + ")\n")
        for st in self.states:
            st.Write(writer)
        writer.ofh.write(" )")

class IState(object):
    def __init__(self, tab):
        self.tab = tab
        self.insns = []
        self.id = -1

    def Write(self, writer):
        writer.ofh.write("  (STATE " + str(self.id) + "\n")
        for insn in self.insns:
            insn.Write(writer)
        writer.ofh.write("  )\n")

class IInsn(object):
    def __init__(self, resource):
        self.id = -1
        self.inputs = []
        self.outputs = []
        self.target_states = []
        self.resource = resource

    def Write(self, writer):
        writer.ofh.write("   (INSN " + str(self.id) + " ")
        writer.ofh.write(self.resource.resource_class.name + " ")
        writer.ofh.write(str(self.resource.id) + " () ")
        # transitions, inputs, outputs
        self.writeIds(writer, self.target_states)
        writer.ofh.write(" ")
        self.writeIds(writer, self.inputs)
        writer.ofh.write(" ")
        self.writeIds(writer, self.outputs)
        writer.ofh.write(")\n")

    def writeIds(self, writer, objs):
        """objs can be list of either IState or IRegister."""
        writer.ofh.write("(")
        writer.ofh.write(" ".join([str(o.id) for o in objs]))
        writer.ofh.write(")")

class IRegister(object):
    def __init__(self, table, name):
        table.registers.append(self)
        self.id = -1
        self.name = name
        self.initialValue = None
        self.valueType = IValueType(32)
        self.isConst = False

    def Write(self, writer):
        writer.ofh.write("    (REGISTER " + str(self.id) + " ")
        if self.name:
            writer.ofh.write(self.name)
        else:
            writer.ofh.write("()")
        writer.ofh.write("\n")
        writer.ofh.write("     ")
        if self.isConst:
            writer.ofh.write("CONST")
        else:
            writer.ofh.write("REG")
        writer.ofh.write(" UINT " + str(self.valueType.width) + " ")
        if self.initialValue:
            self.initialValue.Write(writer)
        else:
            writer.ofh.write("()")
        writer.ofh.write("\n")
        writer.ofh.write("    )\n")

    def SetInitialValue(self, int_val):
        self.initialValue = IValue(int_val)

class IResource(object):
    def __init__(self, table, resource_class):
        self.table = table
        self.resource_class = resource_class
        self.id = -1
        self.array = None
        self.input_types = []
        self.output_types = []
        self.resource_params = ResourceParams()

    def Write(self, writer):
        writer.ofh.write("   (RESOURCE " + str(self.id))
        writer.ofh.write(" " + self.resource_class.name + "\n")
        # input, output, params
        writer.ofh.write("    ")
        self.writeWidths(writer, self.input_types)
        writer.ofh.write(" ")
        self.writeWidths(writer, self.output_types)
        writer.ofh.write("\n")
        writer.ofh.write("    ")
        self.resource_params.Write(writer)
        if self.array:
            self.array.Write(writer)
        writer.ofh.write("   )\n")

    def writeWidths(self, writer, types):
        writer.ofh.write("(")
        writer.ofh.write(" ".join([" UINT " + str(t.width) for t in types]))
        writer.ofh.write(")")

class IResourceClass(object):
    def __init__(self, name):
        self.name = name

class IValue(object):
    def __init__(self, int_val):
        self.val = int_val

    def Write(self, writer):
        writer.ofh.write(str(self.val))

class IValueType(object):
    def __init__(self, width):
        self.width = width

class IArray(object):
    def __init__(self, address_width, data_type, is_external, is_ram):
        self.address_width = address_width
        self.data_type = data_type
        self.is_external = is_external
        self.is_ram = is_ram

    def Write(self, writer):
        writer.ofh.write("    (ARRAY " + str(self.address_width))
        writer.ofh.write(" UINT " + str(self.data_type.width))
        if self.is_external:
            writer.ofh.write(" EXTERNAL")
        else:
            writer.ofh.write(" INTERNAL")
        if self.is_ram:
            writer.ofh.write(" RAM")
        else:
            writer.ofh.write(" ROM")
        writer.ofh.write(")\n")

class ResourceParams(object):
    def __init__(self):
        self.params = dict()

    def AddValue(self, key, value):
        if not key in self.params:
            self.params[key] = []
        self.params[key].append(value)

    def Write(self, writer):
        writer.ofh.write("(PARAMS ")
        kvs = []
        for k, values in self.params.iteritems():
            kv = "(" + k + " " + (" ".join(v for v in values)) + ")"
            kvs.append(kv)
        writer.ofh.write(" ".join(kv for kv in kvs))
        writer.ofh.write(")\n")

# IChannel
    
class DesignWriter(object):
    def __init__(self, design):
        self.design = design
        self.ofh = sys.stdout

    def Write(self):
        self.design.Write(self)

class DesignTool(object):
    @classmethod
    def GetResource(cls, table, name):
        design = table.module.design
        rc = design.findResourceClassByName(name)
        for res in table.resources:
            if res.resource_class == rc:
                return res
        res = IResource(table, rc)
        table.resources.append(res)
        return res

    @classmethod
    def GetBinOpResource(cls, table, name, width):
        design = table.module.design
        rc = design.findResourceClassByName(name)
        for res in table.resources:
            if res.resource_class == rc:
                if res.input_types[0].width == width:
                    return res
        res = IResource(table, rc)
        t = IValueType(width)
        res.input_types.append(t)
        res.input_types.append(t)
        if name == "gt":
            res.output_types.append(IValueType(0))
        else:
            res.output_types.append(t)
        table.resources.append(res)
        return res

    @classmethod
    def ValidateIds(cls, design):
        for mod in design.modules:
            cls.doValidateIds(mod.tables)
            for tab in mod.tables:
                insns = []
                cls.doValidateIds(tab.resources)
                cls.doValidateIds(tab.registers)
                cls.doValidateIds(tab.states)
                for st in tab.states:
                    for insn in st.insns:
                        insns.append(insn)
                cls.doValidateIds(insns)

    @classmethod
    def doValidateIds(cls, objs):
        usedIds = set()
        for obj in objs:
            if obj.id != -1:
                usedIds.add(obj.id)
        unusedId = 1
        for obj in objs:
            if obj.id != -1:
                continue
            while unusedId in usedIds:
                unusedId = unusedId + 1
            obj.id = unusedId
            unusedId = unusedId + 1

    @classmethod
    def CreateArrayResource(cls, table, addr_width, data_width, is_external, is_ram):
        data_type = IValueType(data_width)
        res = cls.GetResource(table, "array")
        res.array = IArray(addr_width, data_type, is_external, is_ram)
        return res

    @classmethod
    def AllocConstNum(cls, table, width, val):
        reg = IRegister(table, "")
        reg.initialValue = IValue(val)
        reg.valueType = IValueType(width)
        reg.isConst = True
        return reg

    @classmethod
    def AddNextState(cls, st1, st2):
        tr = cls.GetResource(st1.tab, "tr")
        tr_insn = None
        for insn in st1.insns:
            if insn.resource == tr:
                tr_insn = insn
        if not tr_insn:
            tr_insn = IInsn(tr)
            st1.insns.append(tr_insn)
        tr_insn.target_states.append(st2)
        return tr_insn

    @classmethod
    def CreateEmbedResource(cls, table, name, fn):
        design = table.module.design
        rc = design.findResourceClassByName("embedded")
        res = IResource(table, rc)
        res.resource_params.AddValue("EMBEDDED-MODULE", name)
        res.resource_params.AddValue("EMBEDDED-MODULE-FILE", fn)
        table.resources.append(res)
        return res
