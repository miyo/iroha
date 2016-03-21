from iroha import *

d = IDesign()
mod = IModule(d, "mod")
tab = ITable(mod)
st1 = IState(tab)
tab.initialSt = st1

r1 = IRegister(tab, "r1")
r2 = IRegister(tab, "r2")

r2.SetInitialValue(123)

assign = DesignTool.GetResource(tab, "set")
insn = IInsn(assign)
insn.inputs.append(r2)
insn.outputs.append(r1)
st1.insns.append(insn)

DesignTool.ValidateIds(d)

w = DesignWriter(d)
w.Write()
