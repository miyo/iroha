#include "iroha/resource_class.h"

#include "design/object_pool.h"
#include "iroha/i_design.h"
#include "iroha/resource_class.h"

namespace iroha {
namespace resource {

bool IsExclusiveBinOp(const IResourceClass &rc) {
  return IsNumToNumExclusiveBinOp(rc) ||
    IsNumToBoolExclusiveBinOp(rc);
}

bool IsNumToNumExclusiveBinOp(const IResourceClass &rc) {
  const string &name = rc.GetName();
  return (name == kAdd || name == kSub);
}

bool IsNumToBoolExclusiveBinOp(const IResourceClass &rc) {
  return (rc.GetName() == kGt);
}

bool IsLightBinOp(const IResourceClass &rc) {
  const string &name = rc.GetName();
  return (name == kBitAnd || name == kBitOr || name == kBitXor);
}

bool IsBitArrangeOp(const IResourceClass &rc) {
  return (rc.GetName() == kShift);
}

bool IsArray(const IResourceClass &rc) {
  return (rc.GetName() == kArray);
}

bool IsMapped(const IResourceClass &rc) {
  return (rc.GetName() == kMapped);
}

bool IsSubModuleTaskCall(const IResourceClass &rc) {
  return (rc.GetName() == kSubModuleTaskCall);
}

bool IsSubModuleTask(const IResourceClass &rc) {
  return (rc.GetName() == kSubModuleTask);
}

static void InstallResource(IDesign *design, const string &name,
			    bool is_exclusive) {
  IResourceClass *klass = new IResourceClass(name, is_exclusive, design);
  design->resource_classes_.push_back(klass);
  ObjectPool *pool = design->GetObjectPool();
  pool->resource_classes_.Add(klass);
}

void InstallResourceClasses(IDesign *design) {
  InstallResource(design, resource::kSet, false);
  InstallResource(design, resource::kPhi, false);
  InstallResource(design, resource::kSelect, false);
  InstallResource(design, resource::kPrint, false);
  InstallResource(design, resource::kAssert, false);
  InstallResource(design, resource::kMapped, true);
  InstallResource(design, resource::kChannelWrite, true);
  InstallResource(design, resource::kChannelRead, false);
  InstallResource(design, resource::kSubModuleTaskCall, true);
  InstallResource(design, resource::kSubModuleTask, true);
  InstallResource(design, resource::kTransition, true);
  InstallResource(design, resource::kEmbedded, true);
  InstallResource(design, resource::kExtInput, true);
  InstallResource(design, resource::kExtOutput, true);
  InstallResource(design, resource::kArray, true);
  InstallResource(design, resource::kGt, true);
  InstallResource(design, resource::kAdd, true);
  InstallResource(design, resource::kSub, true);
  InstallResource(design, resource::kBitAnd, false);
  InstallResource(design, resource::kBitOr, false);
  InstallResource(design, resource::kBitXor, false);
  InstallResource(design, resource::kShift, false);
}

}  // namespace resource
}  // namespace iroha
