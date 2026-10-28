# scripts/update_review2_slides.py
import zipfile
import shutil
import os
import xml.etree.ElementTree as ET

PPTX_PATH = "Review2- Simulation-final.pptx"
BACKUP_PATH = "Review2- Simulation-final.backup.pptx"
TEMP_PPTX = "Review2- Simulation-final.temp.pptx"

# Ensure backup exists
if not os.path.exists(BACKUP_PATH):
    shutil.copyfile(PPTX_PATH, BACKUP_PATH)
    print("Created backup at", BACKUP_PATH)

def make_slide3_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg>
      <p:bgPr>
        <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
        <a:effectLst/>
      </p:bgPr>
    </p:bg>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      
      <!-- Slide Title -->
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="2" name="TextBox 1"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="548640" y="320040"/>
            <a:ext cx="11064240" cy="707886"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square"><a:spAutoFit/></a:bodyPr>
          <a:lstStyle/>
          <a:p>
            <a:pPr algn="l">
              <a:spcAft><a:spcPts val="600"/></a:spcAft>
            </a:pPr>
            <a:r>
              <a:rPr sz="4000" b="1" dirty="0">
                <a:solidFill><a:srgbClr val="000000"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Recap and Review 1 Feedback Overview</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>
      
      <!-- Slide Content -->
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="3" name="TextBox 2"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="731520" y="1300000"/>
            <a:ext cx="10698480" cy="5100000"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square"><a:spAutoFit/></a:bodyPr>
          <a:lstStyle/>
          
          <!-- Section 1: Recap -->
          <a:p>
            <a:pPr marL="285750" indent="-285750">
              <a:spcBfr><a:spcPts val="400"/></a:spcBfr>
              <a:spcAft><a:spcPts val="200"/></a:spcAft>
              <a:buFont typeface="Arial"/>
              <a:buChar char="&#x25CF;"/>
            </a:pPr>
            <a:r>
              <a:rPr sz="2200" b="1">
                <a:solidFill><a:srgbClr val="1F4E79"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Recap of Review 1 Deliverables:</a:t>
            </a:r>
          </a:p>
          <a:p>
            <a:pPr marL="571500" indent="-285750">
              <a:spcAft><a:spcPts val="200"/></a:spcAft>
              <a:buFont typeface="Arial"/>
              <a:buChar char="&#x25CB;"/>
            </a:pPr>
            <a:r>
              <a:rPr sz="1800" b="0">
                <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Formulated the AMORA architecture for multi-objective source routing across heterogeneous enterprise data.</a:t>
            </a:r>
          </a:p>
          <a:p>
            <a:pPr marL="571500" indent="-285750">
              <a:spcAft><a:spcPts val="300"/></a:spcAft>
              <a:buFont typeface="Arial"/>
              <a:buChar char="&#x25CB;"/>
            </a:pPr>
            <a:r>
              <a:rPr sz="1800" b="0">
                <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Demonstrated initial proof-of-concept pipeline with basic gating and a baseline operational efficiency of ~40%.</a:t>
            </a:r>
          </a:p>

          <!-- Section 2: Feedback Received -->
          <a:p>
            <a:pPr marL="285750" indent="-285750">
              <a:spcBfr><a:spcPts val="400"/></a:spcBfr>
              <a:spcAft><a:spcPts val="200"/></a:spcAft>
              <a:buFont typeface="Arial"/>
              <a:buChar char="&#x25CF;"/>
            </a:pPr>
            <a:r>
              <a:rPr sz="2200" b="1">
                <a:solidFill><a:srgbClr val="C00000"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Panel Feedback &amp; Directives:</a:t>
            </a:r>
          </a:p>
          <a:p>
            <a:pPr marL="571500" indent="-285750">
              <a:spcAft><a:spcPts val="200"/></a:spcAft>
              <a:buFont typeface="Arial"/>
              <a:buChar char="&#x25CB;"/>
            </a:pPr>
            <a:r>
              <a:rPr sz="1800" b="1">
                <a:solidFill><a:srgbClr val="222222"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Feedback 1 (Dataset Uniqueness): </a:t>
            </a:r>
            <a:r>
              <a:rPr sz="1800" b="0">
                <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Develop and deploy proprietary/own datasets to make the research unique rather than relying on generic benchmarks.</a:t>
            </a:r>
          </a:p>
          <a:p>
            <a:pPr marL="571500" indent="-285750">
              <a:spcAft><a:spcPts val="300"/></a:spcAft>
              <a:buFont typeface="Arial"/>
              <a:buChar char="&#x25CB;"/>
            </a:pPr>
            <a:r>
              <a:rPr sz="1800" b="1">
                <a:solidFill><a:srgbClr val="222222"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Feedback 2 (Efficiency Optimization): </a:t>
            </a:r>
            <a:r>
              <a:rPr sz="1800" b="0">
                <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Enhance algorithmic routing mechanics to scale efficiency significantly higher than the previous 40% baseline.</a:t>
            </a:r>
          </a:p>

          <!-- Section 3: Actions & Results -->
          <a:p>
            <a:pPr marL="285750" indent="-285750">
              <a:spcBfr><a:spcPts val="400"/></a:spcBfr>
              <a:spcAft><a:spcPts val="200"/></a:spcAft>
              <a:buFont typeface="Arial"/>
              <a:buChar char="&#x25CF;"/>
            </a:pPr>
            <a:r>
              <a:rPr sz="2200" b="1">
                <a:solidFill><a:srgbClr val="375623"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Review 2 Simulation Milestones Achieved:</a:t>
            </a:r>
          </a:p>
          <a:p>
            <a:pPr marL="571500" indent="-285750">
              <a:spcAft><a:spcPts val="200"/></a:spcAft>
              <a:buFont typeface="Arial"/>
              <a:buChar char="&#x25CB;"/>
            </a:pPr>
            <a:r>
              <a:rPr sz="1800" b="1">
                <a:solidFill><a:srgbClr val="222222"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Curated 55 Specialized Enterprise Catalogs: </a:t>
            </a:r>
            <a:r>
              <a:rPr sz="1800" b="0">
                <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Multi-modal schema mappings spanning SQL, ERP/CRM REST endpoints, and PDF documents.</a:t>
            </a:r>
          </a:p>
          <a:p>
            <a:pPr marL="571500" indent="-285750">
              <a:spcAft><a:spcPts val="200"/></a:spcAft>
              <a:buFont typeface="Arial"/>
              <a:buChar char="&#x25CB;"/>
            </a:pPr>
            <a:r>
              <a:rPr sz="1800" b="1">
                <a:solidFill><a:srgbClr val="222222"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Surpassed 57% System Efficiency: </a:t>
            </a:r>
            <a:r>
              <a:rPr sz="1800" b="0">
                <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Attained 35% retrieval bypass, 26.7% token reduction, and 99.4% candidate pruning with sub-4.2 ms latency.</a:t>
            </a:r>
          </a:p>

        </p:txBody>
      </p:sp>

      <!-- Slide Number -->
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="4" name="SlideNumber"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="11338560" y="6400800"/>
            <a:ext cx="548640" cy="320040"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="none"><a:spAutoFit/></a:bodyPr>
          <a:lstStyle/>
          <a:p>
            <a:pPr algn="r"/>
            <a:r>
              <a:rPr sz="1200" b="0">
                <a:solidFill><a:srgbClr val="000000"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>4</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>

    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''

def make_slide4_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg>
      <p:bgPr>
        <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
        <a:effectLst/>
      </p:bgPr>
    </p:bg>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      
      <!-- Slide Title -->
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="2" name="TextBox 1"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="548640" y="320040"/>
            <a:ext cx="11064240" cy="707886"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square"><a:spAutoFit/></a:bodyPr>
          <a:lstStyle/>
          <a:p>
            <a:pPr algn="l">
              <a:spcAft><a:spcPts val="600"/></a:spcAft>
            </a:pPr>
            <a:r>
              <a:rPr sz="4000" b="1" dirty="0">
                <a:solidFill><a:srgbClr val="000000"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>Review 1 Comments and Actions Taken</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>

      <!-- Table Frame -->
      <p:graphicFrame>
        <p:nvGraphicFramePr>
          <p:cNvPr id="3" name="Table 2"/>
          <p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr>
          <p:nvPr/>
        </p:nvGraphicFramePr>
        <p:xfrm>
          <a:off x="563880" y="1450000"/>
          <a:ext cx="11064240" cy="4500000"/>
        </p:xfrm>
        <a:graphic>
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">
            <a:tbl>
              <a:tblPr firstRow="1" bandRow="1">
                <a:tableStyleId>{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}</a:tableStyleId>
              </a:tblPr>
              <a:tblGrid>
                <a:gridCol w="3500000"/>
                <a:gridCol w="5564240"/>
                <a:gridCol w="2000000"/>
              </a:tblGrid>
              
              <!-- Header Row -->
              <a:tr h="800000">
                <a:tc>
                  <a:txBody>
                    <a:bodyPr anchor="ctr"/>
                    <a:lstStyle/>
                    <a:p>
                      <a:pPr algn="ctr"/>
                      <a:r>
                        <a:rPr sz="2200" b="1">
                          <a:solidFill><a:schemeClr val="bg1"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>Panel Comment</a:t>
                      </a:r>
                    </a:p>
                  </a:txBody>
                  <a:tcPr/>
                </a:tc>
                <a:tc>
                  <a:txBody>
                    <a:bodyPr anchor="ctr"/>
                    <a:lstStyle/>
                    <a:p>
                      <a:pPr algn="ctr"/>
                      <a:r>
                        <a:rPr sz="2200" b="1">
                          <a:solidFill><a:schemeClr val="bg1"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>Action Taken</a:t>
                      </a:r>
                    </a:p>
                  </a:txBody>
                  <a:tcPr/>
                </a:tc>
                <a:tc>
                  <a:txBody>
                    <a:bodyPr anchor="ctr"/>
                    <a:lstStyle/>
                    <a:p>
                      <a:pPr algn="ctr"/>
                      <a:r>
                        <a:rPr sz="2200" b="1">
                          <a:solidFill><a:schemeClr val="bg1"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>Status</a:t>
                      </a:r>
                    </a:p>
                  </a:txBody>
                  <a:tcPr/>
                </a:tc>
              </a:tr>

              <!-- Row 1: Dataset Uniqueness -->
              <a:tr h="1800000">
                <a:tc>
                  <a:txBody>
                    <a:bodyPr anchor="ctr"/>
                    <a:lstStyle/>
                    <a:p>
                      <a:pPr algn="l">
                        <a:spcAft><a:spcPts val="400"/></a:spcAft>
                      </a:pPr>
                      <a:r>
                        <a:rPr sz="1600" b="1">
                          <a:solidFill><a:srgbClr val="000000"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>Use Own / Domain-Specific Datasets:</a:t>
                      </a:r>
                    </a:p>
                    <a:p>
                      <a:pPr algn="l"/>
                      <a:r>
                        <a:rPr sz="1500" b="0">
                          <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>The panel advised utilizing proprietary/custom datasets to make the system unique rather than relying solely on generic standard public benchmarks.</a:t>
                      </a:r>
                    </a:p>
                  </a:txBody>
                  <a:tcPr/>
                </a:tc>
                <a:tc>
                  <a:txBody>
                    <a:bodyPr anchor="ctr"/>
                    <a:lstStyle/>
                    <a:p>
                      <a:pPr algn="l">
                        <a:spcAft><a:spcPts val="400"/></a:spcAft>
                      </a:pPr>
                      <a:r>
                        <a:rPr sz="1600" b="1">
                          <a:solidFill><a:srgbClr val="1F4E79"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>Developed 55 Heterogeneous Enterprise Catalogs:</a:t>
                      </a:r>
                    </a:p>
                    <a:p>
                      <a:pPr algn="l">
                        <a:spcAft><a:spcPts val="300"/></a:spcAft>
                      </a:pPr>
                      <a:r>
                        <a:rPr sz="1500" b="0">
                          <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>&#x2022; Built 55 multi-modal enterprise source catalogs across relational SQL ledgers (Sales, POS, Ecommerce), REST APIs (CRM, Pricing, HR), and PDF documents.</a:t>
                      </a:r>
                    </a:p>
                    <a:p>
                      <a:pPr algn="l"/>
                      <a:r>
                        <a:rPr sz="1500" b="0">
                          <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>&#x2022; Engineered custom domain schemas and multi-objective metadata profiles for end-to-end evaluation.</a:t>
                      </a:r>
                    </a:p>
                  </a:txBody>
                  <a:tcPr/>
                </a:tc>
                <a:tc>
                  <a:txBody>
                    <a:bodyPr anchor="ctr"/>
                    <a:lstStyle/>
                    <a:p>
                      <a:pPr algn="ctr"/>
                      <a:r>
                        <a:rPr sz="1600" b="1">
                          <a:solidFill><a:srgbClr val="375623"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>Completed&#x0A;(55 Catalogs Deployed)</a:t>
                      </a:r>
                    </a:p>
                  </a:txBody>
                  <a:tcPr/>
                </a:tc>
              </a:tr>

              <!-- Row 2: Efficiency Increase -->
              <a:tr h="1800000">
                <a:tc>
                  <a:txBody>
                    <a:bodyPr anchor="ctr"/>
                    <a:lstStyle/>
                    <a:p>
                      <a:pPr algn="l">
                        <a:spcAft><a:spcPts val="400"/></a:spcAft>
                      </a:pPr>
                      <a:r>
                        <a:rPr sz="1600" b="1">
                          <a:solidFill><a:srgbClr val="000000"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>Increase System Efficiency (%):</a:t>
                      </a:r>
                    </a:p>
                    <a:p>
                      <a:pPr algn="l"/>
                      <a:r>
                        <a:rPr sz="1500" b="0">
                          <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>The panel instructed to increase operational efficiency from the initial 40% baseline to a substantially higher, production-grade percentage.</a:t>
                      </a:r>
                    </a:p>
                  </a:txBody>
                  <a:tcPr/>
                </a:tc>
                <a:tc>
                  <a:txBody>
                    <a:bodyPr anchor="ctr"/>
                    <a:lstStyle/>
                    <a:p>
                      <a:pPr algn="l">
                        <a:spcAft><a:spcPts val="400"/></a:spcAft>
                      </a:pPr>
                      <a:r>
                        <a:rPr sz="1600" b="1">
                          <a:solidFill><a:srgbClr val="1F4E79"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>Surpassed 57% System Efficiency Metric:</a:t>
                      </a:r>
                    </a:p>
                    <a:p>
                      <a:pPr algn="l">
                        <a:spcAft><a:spcPts val="300"/></a:spcAft>
                      </a:pPr>
                      <a:r>
                        <a:rPr sz="1500" b="0">
                          <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>&#x2022; Integrated INKER Knowledge Retrieval Trigger (IE-KRT), bypassing 35.0% of unneeded retrievals.</a:t>
                      </a:r>
                    </a:p>
                    <a:p>
                      <a:pPr algn="l">
                        <a:spcAft><a:spcPts val="300"/></a:spcAft>
                      </a:pPr>
                      <a:r>
                        <a:rPr sz="1500" b="0">
                          <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>&#x2022; Evidence Fusion reduced prompt token bloat by 26.7% (786 vs 1,073 tokens).</a:t>
                      </a:r>
                    </a:p>
                    <a:p>
                      <a:pPr algn="l"/>
                      <a:r>
                        <a:rPr sz="1500" b="0">
                          <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>&#x2022; Two-stage funnel achieved &gt;99.4% Source Reduction Ratio (SRR) with 3.26 ms routing latency.</a:t>
                      </a:r>
                    </a:p>
                  </a:txBody>
                  <a:tcPr/>
                </a:tc>
                <a:tc>
                  <a:txBody>
                    <a:bodyPr anchor="ctr"/>
                    <a:lstStyle/>
                    <a:p>
                      <a:pPr algn="ctr"/>
                      <a:r>
                        <a:rPr sz="1600" b="1">
                          <a:solidFill><a:srgbClr val="375623"/></a:solidFill>
                          <a:latin typeface="Times New Roman"/>
                        </a:rPr>
                        <a:t>Completed&#x0A;(&gt;57% Efficiency Achieved)</a:t>
                      </a:r>
                    </a:p>
                  </a:txBody>
                  <a:tcPr/>
                </a:tc>
              </a:tr>

            </a:tbl>
          </a:graphicData>
        </a:graphic>
      </p:graphicFrame>

      <!-- Slide Number -->
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="4" name="SlideNumber"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="11338560" y="6400800"/>
            <a:ext cx="548640" cy="320040"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="none"><a:spAutoFit/></a:bodyPr>
          <a:lstStyle/>
          <a:p>
            <a:pPr algn="r"/>
            <a:r>
              <a:rPr sz="1200" b="0">
                <a:solidFill><a:srgbClr val="000000"/></a:solidFill>
                <a:latin typeface="Times New Roman"/>
              </a:rPr>
              <a:t>5</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>

    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''

def update_pptx():
    s3_new = make_slide3_xml().encode('utf-8')
    s4_new = make_slide4_xml().encode('utf-8')
    
    with zipfile.ZipFile(BACKUP_PATH, 'r') as zin:
        with zipfile.ZipFile(TEMP_PPTX, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == 'ppt/slides/slide3.xml':
                    zout.writestr(item, s3_new)
                elif item.filename == 'ppt/slides/slide4.xml':
                    zout.writestr(item, s4_new)
                else:
                    zout.writestr(item, zin.read(item.filename))
                    
    shutil.move(TEMP_PPTX, PPTX_PATH)
    print("Successfully updated Review2- Simulation-final.pptx!")

if __name__ == "__main__":
    update_pptx()
