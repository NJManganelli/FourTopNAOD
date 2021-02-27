import ROOT
# import lhapdf

# ROOT.gROOT.ProcessLine(".L /cvmfs/cms.cern.ch/slc7_amd64_gcc700/external/lhapdf/6.2.1-gnimlf3/lib/libLHAPDF.so")
# ROOT.gSystem.Load("/cvmfs/cms.cern.ch/slc7_amd64_gcc700/external/lhapdf/6.2.1-gnimlf3/lib/libLHAPDF.so")
ROOT.gROOT.ProcessLine(".L LHAPDF.cpp")

#Look at tttt sample
fin = ROOT.TFile.Open("tttt_2018_ElMu_test.root", "read")
tin = fin.Get("Events")
tin.GetEntry(0)

#Load the stored pdf variation (not the generated one!
p = ROOT.LHAPDF.getPDFSet("PDF4LHC15_nnlo_30_pdfas")
p2 = p.mkPDFs()
# LHAPDF 6.3.0 loading all 33 PDFs in set PDF4LHC15_nnlo_30_pdfas
# PDF4LHC15_nnlo_30_pdfas, version 2; 33 PDF members
#Calculate the nominal stored pdf value
pdf_nom = p2[0].xfxQ(tin.Generator_id1, tin.Generator_x1, tin.Generator_scalePDF) * p2[0].xfxQ(tin.Generator_id2, tin.Generator_x2, tin.Generator_scalePDF)
# 0.4457617376899627
#Get the stored pdf variation, which is divided by the generator nominal variation presumably...
pdf_nom_divided_by_gen_pdf_nom = tin.LHEPdfWeight[0]
# 1.13299560546875
#Get the first stored variation
pdf_1 = tin.LHEPdfWeight[1]
# 1.10894775390625
#Find the gen_pdf_nom
p2[0].xfxQ(tin.Generator_id1, tin.Generator_x1, tin.Generator_scalePDF) * p2[0].xfxQ(tin.Generator_id2, tin.Generator_x2, tin.Generator_scalePDF)/1.13299
# 0.3934383689970456
#lhepdfweight[1] * gen_pdf_nom = pdf[1] value we'll calculate...
#1.10894775390625 * 0.3934383689970456 = 0.4363025955998121
#Calculate the pdf[1] value
p2[1].xfxQ(tin.Generator_id1, tin.Generator_x1, tin.Generator_scalePDF) * p2[1].xfxQ(tin.Generator_id2, tin.Generator_x2, tin.Generator_scalePDF)
# 0.4367998619912069
#Matches! 

#NOTE: Added the following the the setup environment (e.g. for rdf with LCG_98python3:
	# source /cvmfs/sft.cern.ch/lcg/views/LCG_98python3/x86_64-centos7-gcc8-opt/setup.sh;
	# export LHAPDF_PATH=/cvmfs/sft.cern.ch/lcg/releases/LCG_98python3/MCGenerators/lhapdf/6.3.0/x86_64-centos7-gcc8-opt
	# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$LHAPDF_PATH/lib/
	# export LHAPDF_DATA_PATH=/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current/:${LHAPDF_PATH}/share/LHAPDF

