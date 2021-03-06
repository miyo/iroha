// -*- C++ -*-
#ifndef _writer_html_writer_h_
#define _writer_html_writer_h_

#include "iroha/common.h"

namespace iroha {

namespace opt {
class DebugAnnotation;
}  // namespace opt

class HtmlWriter {
public:
  HtmlWriter(const IDesign *design, ostream &os);

  void Write();
  void WriteIntermediateTable(const ITable &tab);

private:
  void WriteHeader();
  void WriteFooter();
  void WriteModule(const IModule &mod);
  void WriteTable(const ITable &tab);
  void WriteState(const IState &st);
  void WriteInsn(const IInsn &insn);
  void WriteRegisters(const ITable &tab);
  void WriteRegister(const IRegister &reg);
  void WriteResources(const ITable &tab);
  void WriteResource(const IResource &res);
  void WriteValue(const IValue &val);

  const IDesign *design_;
  ostream &os_;
  const opt::DebugAnnotation *annotation_;
};

}  // namespace iroha

#endif  // _writer_html_writer_h_
