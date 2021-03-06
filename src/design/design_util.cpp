#include "design/design_util.h"

#include "iroha/i_design.h"
#include "iroha/resource_class.h"
#include "iroha/logging.h"

namespace iroha {

IModule *DesignUtil::GetRootModule(const IDesign *design) {
  IModule *root = nullptr;
  for (auto *mod : design->modules_) {
    if (mod->GetParentModule() == nullptr) {
      if (root == nullptr) {
	root = mod;
      } else {
	// Don't allow multiple roots.
	return nullptr;
      }
    }
  }
  return root;
}

vector<IModule *> DesignUtil::GetChildModules(const IModule *parent) {
  const IDesign *design = parent->GetDesign();
  vector<IModule *> v;
  for (auto *mod : design->modules_) {
    if (mod->GetParentModule() == parent) {
      v.push_back(mod);
    }
  }
  return v;
}

IResourceClass *DesignUtil::GetTransitionResourceClassFromDesign(IDesign *design) {
  for (auto *rc : design->resource_classes_) {
    if (rc->GetName() == resource::kTransition) {
      return rc;
    }
  }
  CHECK(false) << "Transition resource class is not installed?";
  return nullptr;
}

IResource *DesignUtil::FindResourceByClassName(ITable *table,
					       const string &name) {
  for (auto *res : table->resources_) {
    if (res->GetClass()->GetName() == name) {
      return res;
    }
  }
  return nullptr;
}

IResource *DesignUtil::FindAssignResource(ITable *table) {
  return FindResourceByClassName(table, resource::kSet);
}

IResource *DesignUtil::FindTransitionResource(ITable *table) {
  return FindResourceByClassName(table, resource::kTransition);
}

IInsn *DesignUtil::FindInsnByResource(IState *state, IResource *res) {
  for (auto *insn : state->insns_) {
    if (insn->GetResource() == res) {
      return insn;
    }
  }
  return nullptr;
}

IResourceClass *DesignUtil::FindResourceClass(IDesign *design,
					      const string &class_name) {
  for (auto *rc : design->resource_classes_) {
    if (rc->GetName() == class_name) {
      return rc;
    }
  }
  return nullptr;
}

IResource *DesignUtil::CreateResource(ITable *table, const string &name) {
  IDesign *design = table->GetModule()->GetDesign();
  IResourceClass *rc = FindResourceClass(design, name);
  if (rc == nullptr) {
    return nullptr;
  }
  IResource *res = new IResource(table, rc);
  table->resources_.push_back(res);
  return res;
}

IInsn *DesignUtil::FindTransitionInsn(IState *st) {
  ITable *table = st->GetTable();
  IResource *tr = DesignUtil::FindResourceByClassName(table,
						      resource::kTransition);
  return DesignUtil::FindInsnByResource(st, tr);
}

IInsn *DesignUtil::GetTransitionInsn(IState *st) {
  IInsn *insn = FindTransitionInsn(st);
  if (insn == nullptr) {
    ITable *table = st->GetTable();
    IResource *tr = DesignUtil::FindResourceByClassName(table,
							resource::kTransition);
    insn = new IInsn(tr);
    st->insns_.push_back(insn);
  }
  return insn;
}

IInsn *DesignUtil::FindTaskEntryInsn(ITable *table) {
  IResource *res = FindResourceByClassName(table, resource::kSubModuleTask);
  if (res == nullptr) {
    return nullptr;
  }
  return DesignUtil::FindInsnByResource(table->GetInitialState(), res);
}

bool DesignUtil::IsTerminalState(IState *st) {
  ITable *table = st->GetTable();
  IResource *tr = DesignUtil::FindTransitionResource(table);
  IInsn *insn = DesignUtil::FindInsnByResource(st, tr);
  if (insn == nullptr) {
    return true;
  }
  if (insn->target_states_.size() == 0) {
    return true;
  }
  return false;
}

bool DesignUtil::IsMultiCycleInsn(IInsn *insn) {
  IResource *res = insn->GetResource();
  IResourceClass *rc = res->GetClass();
  if (resource::IsSubModuleTaskCall(*rc)) {
    return true;
  }
  return false;
}

bool DesignUtil::IsMultiCycleState(IState *st) {
  for (IInsn *insn : st->insns_) {
    if (IsMultiCycleInsn(insn)) {
      return true;
    }
  }
  return false;
}

}  // namespace iroha
