INP_SECTIONS = {
    "INFILTRATION": {
        "description": "Infiltration parameters for each subcatchment",
        "methods": {
            "Green-Ampt": {
                "fields": [
                    {"name": "Subcatchment", "description": "Subcatchment name", "type": "str"},
                    {"name": "Suction", "description": "Soil capillary suction head", "unit": "in or mm"},
                    {"name": "Ksat", "description": "Saturated hydraulic conductivity", "unit": "in/hr or mm/hr"},
                    {"name": "IMD", "description": "Initial moisture deficit (fraction)", "unit": "fraction"},
                ],
                "example": "Sub1  3.5  0.5  0.26",
            },
            "Horton": {
                "fields": [
                    {"name": "Subcatchment", "description": "Subcatchment name", "type": "str"},
                    {"name": "MaxRate", "description": "Maximum infiltration rate", "unit": "in/hr or mm/hr"},
                    {"name": "MinRate", "description": "Minimum infiltration rate", "unit": "in/hr or mm/hr"},
                    {"name": "Decay", "description": "Decay constant", "unit": "1/hr"},
                    {"name": "DryTime", "description": "Time for fully dry soil", "unit": "days"},
                    {"name": "MaxInfil", "description": "Maximum infiltration volume", "unit": "in or mm (0=unlimited)"},
                ],
                "example": "Sub1  3.0  0.5  4.14  7  0",
            },
            "Curve Number": {
                "fields": [
                    {"name": "Subcatchment", "description": "Subcatchment name", "type": "str"},
                    {"name": "CurveNum", "description": "SCS Curve Number", "unit": "dimensionless"},
                    {"name": "Ksat", "description": "Saturated hydraulic conductivity (0=default)", "unit": "in/hr or mm/hr"},
                    {"name": "DryTime", "description": "Time for fully dry soil", "unit": "days"},
                ],
                "example": "Sub1  80  0.5  7",
            },
        },
        "keywords": ["infiltration", "green-ampt", "horton", "curve number", "suction", "conductivity", "moisture deficit", "pervious", "soil"],
    },
    "SUBCATCHMENTS": {
        "description": "Basic subcatchment properties",
        "fields": [
            {"name": "Name", "description": "Subcatchment name", "type": "str"},
            {"name": "RainGage", "description": "Associated rain gage", "type": "str"},
            {"name": "Outlet", "description": "Outlet node or subcatchment", "type": "str"},
            {"name": "Area", "description": "Subcatchment area", "unit": "acres or hectares"},
            {"name": "PctImperv", "description": "Percent impervious", "unit": "%"},
            {"name": "Width", "description": "Characteristic width of overland flow", "unit": "ft or m"},
            {"name": "Slope", "description": "Average surface slope", "unit": "%"},
            {"name": "CurbLen", "description": "Curb length (for pollutant buildup)", "unit": "ft or m"},
            {"name": "SnowPack", "description": "Snow pack name (optional)", "type": "str"},
        ],
        "example": "Sub1  RG1  J1  5.0  25  500  0.5  0",
        "keywords": ["subcatchment", "area", "impervious", "width", "slope", "overland flow", "runoff", "curb"],
    },
    "SUBAREAS": {
        "description": "Subcatchment subarea parameters for impervious/pervious surfaces",
        "fields": [
            {"name": "Subcatchment", "description": "Subcatchment name", "type": "str"},
            {"name": "N-Imperv", "description": "Manning's N for impervious area", "unit": "dimensionless"},
            {"name": "N-Perv", "description": "Manning's N for pervious area", "unit": "dimensionless"},
            {"name": "S-Imperv", "description": "Depression storage for impervious area", "unit": "in or mm"},
            {"name": "S-Perv", "description": "Depression storage for pervious area", "unit": "in or mm"},
            {"name": "PctZero", "description": "Percent of impervious area with no depression storage", "unit": "%"},
            {"name": "RouteTo", "description": "Internal routing (IMPERVIOUS, PERVIOUS, or OUTLET)", "type": "str"},
            {"name": "PctRouted", "description": "Percent of runoff routed between subareas", "unit": "%"},
        ],
        "example": "Sub1  0.01  0.1  0.05  0.05  25  OUTLET",
        "keywords": ["subarea", "manning", "roughness", "depression storage", "impervious", "pervious", "runoff", "overland"],
    },
    "JUNCTIONS": {
        "description": "Junction node properties",
        "fields": [
            {"name": "Name", "description": "Junction name", "type": "str"},
            {"name": "Elevation", "description": "Invert elevation", "unit": "ft or m"},
            {"name": "MaxDepth", "description": "Maximum water depth (surcharge depth)", "unit": "ft or m"},
            {"name": "InitDepth", "description": "Initial water depth", "unit": "ft or m"},
            {"name": "SurDepth", "description": "Surcharge depth (ponding)", "unit": "ft or m"},
            {"name": "Aponded", "description": "Ponded surface area when flooded", "unit": "ft² or m²"},
        ],
        "example": "J1  100.0  6.0  0  0  0",
        "keywords": ["junction", "node", "manhole", "invert", "elevation", "surcharge", "ponding", "depth", "flooding"],
    },
    "OUTFALLS": {
        "description": "Outfall node properties (system boundaries)",
        "fields": [
            {"name": "Name", "description": "Outfall name", "type": "str"},
            {"name": "Elevation", "description": "Invert elevation", "unit": "ft or m"},
            {"name": "Type", "description": "FREE, NORMAL, FIXED, TIDAL, or TIMESERIES", "type": "str"},
            {"name": "StageData", "description": "Fixed stage, tidal curve, or time series name", "type": "str"},
            {"name": "Gated", "description": "YES or NO for tide gate", "type": "str"},
        ],
        "example": 'Out1  90.0  FREE  NO',
        "keywords": ["outfall", "outlet", "boundary", "free", "normal", "fixed", "tidal", "tide gate"],
    },
    "CONDUITS": {
        "description": "Conduit link properties (pipes and channels)",
        "fields": [
            {"name": "Name", "description": "Conduit name", "type": "str"},
            {"name": "FromNode", "description": "Upstream node", "type": "str"},
            {"name": "ToNode", "description": "Downstream node", "type": "str"},
            {"name": "Length", "description": "Conduit length", "unit": "ft or m"},
            {"name": "Roughness", "description": "Manning's roughness coefficient", "unit": "dimensionless"},
            {"name": "InOffset", "description": "Offset of inlet above node invert", "unit": "ft or m"},
            {"name": "OutOffset", "description": "Offset of outlet above node invert", "unit": "ft or m"},
            {"name": "InitFlow", "description": "Initial flow rate", "unit": "CFS or CMS"},
            {"name": "MaxFlow", "description": "Maximum flow allowed (0=unlimited)", "unit": "CFS or CMS"},
        ],
        "example": "C1  J1  J2  400  0.01  0  0  0  0",
        "keywords": ["conduit", "pipe", "channel", "manning", "roughness", "length", "flow", "offset", "link"],
    },
    "XSECTIONS": {
        "description": "Cross-section geometry for conduits",
        "fields": [
            {"name": "Link", "description": "Link name", "type": "str"},
            {"name": "Shape", "description": "CIRCULAR, RECT_OPEN, RECT_CLOSED, TRAPEZOIDAL, TRIANGULAR, etc.", "type": "str"},
            {"name": "Geom1", "description": "Full height or max depth", "unit": "ft or m"},
            {"name": "Geom2", "description": "Width or top width (0 for circular)", "unit": "ft or m"},
            {"name": "Geom3", "description": "Side slope or other geometry parameter", "unit": "varies"},
            {"name": "Geom4", "description": "Additional geometry parameter", "unit": "varies"},
            {"name": "Barrels", "description": "Number of barrels", "type": "int"},
        ],
        "example": "C1  CIRCULAR  2.0  0  0  0  1",
        "keywords": ["cross section", "xsection", "circular", "rectangular", "trapezoidal", "diameter", "shape", "geometry", "barrel"],
    },
    "PUMPS": {
        "description": "Pump link properties",
        "fields": [
            {"name": "Name", "description": "Pump name", "type": "str"},
            {"name": "FromNode", "description": "Inlet (wet well) node", "type": "str"},
            {"name": "ToNode", "description": "Outlet node", "type": "str"},
            {"name": "PumpCurve", "description": "Name of pump curve", "type": "str"},
            {"name": "Status", "description": "Initial status (ON or OFF)", "type": "str"},
            {"name": "Startup", "description": "Startup depth in wet well", "unit": "ft or m"},
            {"name": "Shutoff", "description": "Shutoff depth in wet well", "unit": "ft or m"},
        ],
        "example": "P1  WetWell  J5  PCurve1  ON  3.0  1.0",
        "keywords": ["pump", "pump curve", "wet well", "lift station", "startup", "shutoff", "force main"],
    },
    "ORIFICES": {
        "description": "Orifice link properties",
        "fields": [
            {"name": "Name", "description": "Orifice name", "type": "str"},
            {"name": "FromNode", "description": "Inlet node", "type": "str"},
            {"name": "ToNode", "description": "Outlet node", "type": "str"},
            {"name": "Type", "description": "SIDE or BOTTOM", "type": "str"},
            {"name": "Offset", "description": "Height offset above node invert", "unit": "ft or m"},
            {"name": "Qcoeff", "description": "Discharge coefficient", "unit": "dimensionless"},
            {"name": "Gated", "description": "YES or NO for flap gate", "type": "str"},
            {"name": "CloseTime", "description": "Time to close (seconds)", "unit": "sec"},
        ],
        "example": "OR1  SU1  J3  SIDE  1.0  0.65  NO  0",
        "keywords": ["orifice", "discharge", "coefficient", "side", "bottom", "flap gate", "outlet"],
    },
    "WEIRS": {
        "description": "Weir link properties",
        "fields": [
            {"name": "Name", "description": "Weir name", "type": "str"},
            {"name": "FromNode", "description": "Inlet node", "type": "str"},
            {"name": "ToNode", "description": "Outlet node", "type": "str"},
            {"name": "Type", "description": "TRANSVERSE, SIDEFLOW, V-NOTCH, TRAPEZOIDAL, ROADWAY", "type": "str"},
            {"name": "CrestHt", "description": "Height of crest above node invert", "unit": "ft or m"},
            {"name": "Qcoeff", "description": "Discharge coefficient", "unit": "dimensionless"},
            {"name": "Gated", "description": "YES or NO for flap gate", "type": "str"},
            {"name": "EndCon", "description": "Number of end contractions", "type": "int"},
            {"name": "EndCoeff", "description": "End contraction discharge coefficient", "unit": "dimensionless"},
            {"name": "Surcharge", "description": "YES or NO to allow surcharge", "type": "str"},
        ],
        "example": "W1  SU1  J4  TRANSVERSE  2.0  3.33  NO  0  0  YES",
        "keywords": ["weir", "transverse", "sideflow", "v-notch", "trapezoidal", "crest", "discharge", "overflow", "diversion"],
    },
    "STORAGE": {
        "description": "Storage unit node properties",
        "fields": [
            {"name": "Name", "description": "Storage unit name", "type": "str"},
            {"name": "Elevation", "description": "Invert elevation", "unit": "ft or m"},
            {"name": "MaxDepth", "description": "Maximum water depth", "unit": "ft or m"},
            {"name": "InitDepth", "description": "Initial water depth", "unit": "ft or m"},
            {"name": "Shape", "description": "TABULAR or FUNCTIONAL", "type": "str"},
            {"name": "CurveName/Coeff", "description": "Storage curve name or coefficient A", "type": "varies"},
            {"name": "Exponent", "description": "Exponent B (for FUNCTIONAL)", "unit": "dimensionless"},
            {"name": "Constant", "description": "Constant C (for FUNCTIONAL)", "unit": "ft² or m²"},
            {"name": "Aponded", "description": "Ponded area when flooded", "unit": "ft² or m²"},
            {"name": "Fevap", "description": "Fraction of potential evaporation realized", "unit": "fraction"},
        ],
        "example": "SU1  95.0  10.0  0  FUNCTIONAL  1000  0  0  0  0",
        "keywords": ["storage", "detention", "pond", "basin", "tank", "reservoir", "volume", "stage", "tabular", "functional"],
    },
    "POLLUTANTS": {
        "description": "Pollutant properties",
        "fields": [
            {"name": "Name", "description": "Pollutant name", "type": "str"},
            {"name": "Units", "description": "Concentration units (MG/L, UG/L, #/L)", "type": "str"},
            {"name": "Crain", "description": "Concentration in rain", "unit": "conc. units"},
            {"name": "Cgw", "description": "Concentration in groundwater", "unit": "conc. units"},
            {"name": "Cii", "description": "Concentration in I&I flow", "unit": "conc. units"},
            {"name": "Kdecay", "description": "First-order decay coefficient", "unit": "1/days"},
            {"name": "SnowOnly", "description": "YES if buildup only during snowfall", "type": "str"},
            {"name": "CoPollutant", "description": "Name of co-pollutant (optional)", "type": "str"},
            {"name": "CoFraction", "description": "Fraction of co-pollutant concentration", "unit": "fraction"},
            {"name": "Cdwf", "description": "Concentration in DWF", "unit": "conc. units"},
            {"name": "Cinit", "description": "Initial concentration throughout system", "unit": "conc. units"},
        ],
        "example": "TSS  MG/L  0  0  0  0  NO  *  0  0  0",
        "keywords": ["pollutant", "concentration", "water quality", "TSS", "BOD", "COD", "decay", "rain", "groundwater"],
    },
    "LANDUSES": {
        "description": "Land use categories for pollutant buildup/washoff",
        "fields": [
            {"name": "Name", "description": "Land use name", "type": "str"},
            {"name": "SweepInterval", "description": "Days between street sweeping", "unit": "days"},
            {"name": "Availability", "description": "Fraction of buildup available for sweeping", "unit": "fraction"},
            {"name": "LastSweep", "description": "Days since last sweeping at start", "unit": "days"},
        ],
        "example": "Residential  0  0  0",
        "keywords": ["land use", "buildup", "washoff", "sweeping", "residential", "commercial", "industrial"],
    },
    "BUILDUP": {
        "description": "Pollutant buildup functions for each land use",
        "fields": [
            {"name": "LandUse", "description": "Land use name", "type": "str"},
            {"name": "Pollutant", "description": "Pollutant name", "type": "str"},
            {"name": "FuncType", "description": "POW, EXP, SAT, or EXT", "type": "str"},
            {"name": "C1", "description": "Maximum buildup or scaling factor", "unit": "varies"},
            {"name": "C2", "description": "Rate constant or half-saturation constant", "unit": "varies"},
            {"name": "C3", "description": "Exponent or time series name", "unit": "varies"},
            {"name": "PerUnit", "description": "AREA or CURBLENGTH", "type": "str"},
        ],
        "example": "Residential  TSS  POW  100  1  0.5  AREA",
        "keywords": ["buildup", "pollutant", "power", "exponential", "saturation", "accumulation", "land use"],
    },
    "WASHOFF": {
        "description": "Pollutant washoff functions for each land use",
        "fields": [
            {"name": "LandUse", "description": "Land use name", "type": "str"},
            {"name": "Pollutant", "description": "Pollutant name", "type": "str"},
            {"name": "FuncType", "description": "EXP, RC (Rating Curve), or EMC", "type": "str"},
            {"name": "C1", "description": "Washoff coefficient or EMC value", "unit": "varies"},
            {"name": "C2", "description": "Washoff exponent", "unit": "varies"},
            {"name": "SweepRmvl", "description": "Street sweeping removal efficiency", "unit": "fraction"},
            {"name": "BmpRmvl", "description": "BMP removal efficiency", "unit": "fraction"},
        ],
        "example": "Residential  TSS  EMC  100  0  0  0",
        "keywords": ["washoff", "EMC", "event mean concentration", "rating curve", "exponential", "pollutant", "runoff quality"],
    },
    "LID_CONTROLS": {
        "description": "Low Impact Development control definitions",
        "fields": [
            {"name": "Name", "description": "LID control name", "type": "str"},
            {"name": "Type", "description": "BC (bio-retention), RG (rain garden), GR (green roof), IT (infiltration trench), PP (permeable pavement), RB (rain barrel), VS (vegetative swale), RD (rooftop disconnection)", "type": "str"},
        ],
        "layers": {
            "SURFACE": ["StorHt (in/mm)", "VegFrac (fraction)", "Rough (Manning N)", "Slope (%)", "Xslope"],
            "SOIL": ["Thickness (in/mm)", "Porosity", "FieldCap", "WiltPoint", "Ksat (in/hr)", "Kcoeff", "SuctHead (in/mm)"],
            "PAVEMENT": ["Thickness (in/mm)", "VoidRatio", "Imperv (fraction)", "Permeability (in/hr)", "ClogFactor"],
            "STORAGE": ["Height (in/mm)", "VoidRatio", "Ksat (in/hr)", "ClogFactor"],
            "DRAIN": ["Coeff", "Exponent", "Offset (in/mm)", "Delay (hrs)"],
        },
        "example": "LID1  BC\nLID1  SURFACE  6  0  0.1  1  5\nLID1  SOIL  18  0.5  0.2  0.1  0.5  10  3.5\nLID1  STORAGE  12  0.75  0.5  0\nLID1  DRAIN  0  0.5  0  6",
        "keywords": ["LID", "bioretention", "rain garden", "green roof", "permeable pavement", "rain barrel", "swale", "infiltration trench", "low impact development"],
    },
    "LID_USAGE": {
        "description": "Assignment of LID controls to subcatchments",
        "fields": [
            {"name": "Subcatchment", "description": "Subcatchment name", "type": "str"},
            {"name": "LIDProcess", "description": "LID control name", "type": "str"},
            {"name": "Number", "description": "Number of replicate LID units", "type": "int"},
            {"name": "Area", "description": "Area of each unit", "unit": "ft² or m²"},
            {"name": "Width", "description": "Width of outflow face of each unit", "unit": "ft or m"},
            {"name": "InitSat", "description": "Initial saturation of soil and storage layers", "unit": "%"},
            {"name": "FromImperv", "description": "Percent of impervious area runoff treated", "unit": "%"},
            {"name": "ToPerv", "description": "1 if overflow goes to pervious area, 0 otherwise", "type": "int"},
            {"name": "RptFile", "description": "Optional name of detailed report file", "type": "str"},
        ],
        "example": "Sub1  LID1  5  500  25  0  50  1",
        "keywords": ["LID usage", "subcatchment", "replicate", "area", "width", "impervious", "treated"],
    },
    "GROUNDWATER": {
        "description": "Groundwater flow parameters for each subcatchment",
        "fields": [
            {"name": "Subcatchment", "description": "Subcatchment name", "type": "str"},
            {"name": "Aquifer", "description": "Aquifer name", "type": "str"},
            {"name": "Node", "description": "Receiving groundwater node", "type": "str"},
            {"name": "Esurf", "description": "Surface elevation of subcatchment", "unit": "ft or m"},
            {"name": "A1", "description": "Groundwater flow coefficient", "unit": "varies"},
            {"name": "B1", "description": "Groundwater flow exponent", "unit": "dimensionless"},
            {"name": "A2", "description": "Surface water flow coefficient", "unit": "varies"},
            {"name": "B2", "description": "Surface water flow exponent", "unit": "dimensionless"},
            {"name": "A3", "description": "Combined flow coefficient", "unit": "varies"},
            {"name": "Dsw", "description": "Fixed surface water depth", "unit": "ft or m"},
            {"name": "Egwt", "description": "Threshold groundwater table elevation", "unit": "ft or m"},
        ],
        "example": "Sub1  Aquifer1  J3  120.0  0.001  2  0  0  0  0  *",
        "keywords": ["groundwater", "aquifer", "water table", "baseflow", "lateral flow", "percolation", "subsurface"],
    },
    "AQUIFERS": {
        "description": "Aquifer properties for groundwater modeling",
        "fields": [
            {"name": "Name", "description": "Aquifer name", "type": "str"},
            {"name": "Por", "description": "Soil porosity", "unit": "fraction"},
            {"name": "WP", "description": "Wilting point moisture content", "unit": "fraction"},
            {"name": "FC", "description": "Field capacity moisture content", "unit": "fraction"},
            {"name": "Ksat", "description": "Saturated hydraulic conductivity", "unit": "in/hr or mm/hr"},
            {"name": "Kslope", "description": "Conductivity slope for variable Ksat", "unit": "dimensionless"},
            {"name": "Tslope", "description": "Tension slope for capillary suction", "unit": "dimensionless"},
            {"name": "ETu", "description": "Upper ET fraction", "unit": "fraction"},
            {"name": "ETs", "description": "Lower ET depth", "unit": "ft or m"},
            {"name": "Seep", "description": "Seepage rate to deep groundwater", "unit": "in/hr or mm/hr"},
            {"name": "Ebot", "description": "Elevation of aquifer bottom", "unit": "ft or m"},
            {"name": "Ewt", "description": "Initial water table elevation", "unit": "ft or m"},
            {"name": "Eunsat", "description": "Initial moisture content of unsaturated zone", "unit": "fraction"},
        ],
        "example": "Aquifer1  0.5  0.15  0.3  0.5  10  15  0.35  14  0.002  0  80  0.3",
        "keywords": ["aquifer", "porosity", "wilting point", "field capacity", "conductivity", "water table", "groundwater", "unsaturated"],
    },
    "SNOWPACKS": {
        "description": "Snow pack parameters for snowmelt modeling",
        "fields": [
            {"name": "Name", "description": "Snow pack name", "type": "str"},
            {"name": "Surface", "description": "PLOWABLE, IMPERVIOUS, or PERVIOUS", "type": "str"},
            {"name": "Cmin", "description": "Minimum melt coefficient", "unit": "in/hr/°F or mm/hr/°C"},
            {"name": "Cmax", "description": "Maximum melt coefficient", "unit": "in/hr/°F or mm/hr/°C"},
            {"name": "Tbase", "description": "Base temperature for snowmelt", "unit": "°F or °C"},
            {"name": "FWF", "description": "Free water fraction at which snow becomes wet pack", "unit": "fraction"},
            {"name": "SD0", "description": "Initial snow depth", "unit": "in (water equiv.)"},
            {"name": "FW0", "description": "Initial free water in pack", "unit": "in (water equiv.)"},
        ],
        "example": "SnowPack1  PLOWABLE  0.001  0.003  32  0.1  0  0",
        "keywords": ["snowmelt", "snow pack", "melt coefficient", "cold content", "plowing", "temperature", "free water"],
    },
    "RAINGAGES": {
        "description": "Rain gage properties",
        "fields": [
            {"name": "Name", "description": "Rain gage name", "type": "str"},
            {"name": "Format", "description": "INTENSITY, VOLUME, or CUMULATIVE", "type": "str"},
            {"name": "Interval", "description": "Recording time interval", "unit": "decimal hours or hr:min"},
            {"name": "SCF", "description": "Snow catch deficiency factor", "unit": "dimensionless"},
            {"name": "Source", "description": "TIMESERIES or FILE", "type": "str"},
            {"name": "SeriesName/FileName", "description": "Time series or file name", "type": "str"},
        ],
        "example": "RG1  INTENSITY  0:05  1.0  TIMESERIES  TS1",
        "keywords": ["rain gage", "rainfall", "intensity", "hyetograph", "time series", "precipitation", "recording interval"],
    },
    "DWF": {
        "description": "Dry weather flow (sanitary flow) at nodes",
        "fields": [
            {"name": "Node", "description": "Node name", "type": "str"},
            {"name": "Constituent", "description": "FLOW or pollutant name", "type": "str"},
            {"name": "Baseline", "description": "Average baseline DWF value", "unit": "flow or conc. units"},
            {"name": "Patterns", "description": "Time pattern names (up to 4)", "type": "str"},
        ],
        "example": "J1  FLOW  0.5  DailyPat  HourlyPat",
        "keywords": ["dry weather flow", "sanitary", "base flow", "inflow", "pattern", "diurnal"],
    },
    "RDII": {
        "description": "Rainfall-dependent infiltration/inflow at nodes",
        "fields": [
            {"name": "Node", "description": "Node name", "type": "str"},
            {"name": "UHGroup", "description": "Unit hydrograph group name", "type": "str"},
            {"name": "SewerArea", "description": "Sewer area contributing RDII", "unit": "acres or hectares"},
        ],
        "example": "J1  UH1  10.0",
        "keywords": ["RDII", "infiltration", "inflow", "unit hydrograph", "sewer", "I&I", "rainfall dependent"],
    },
    "OPTIONS": {
        "description": "Analysis options for the simulation",
        "fields": [
            {"name": "FLOW_UNITS", "description": "CFS, GPM, MGD, CMS, LPS, MLD", "type": "str"},
            {"name": "INFILTRATION", "description": "HORTON, GREEN_AMPT, CURVE_NUMBER", "type": "str"},
            {"name": "FLOW_ROUTING", "description": "STEADY, KINWAVE, DYNWAVE", "type": "str"},
            {"name": "LINK_OFFSETS", "description": "DEPTH or ELEVATION", "type": "str"},
            {"name": "FORCE_MAIN_EQUATION", "description": "H-W (Hazen-Williams) or D-W (Darcy-Weisbach)", "type": "str"},
            {"name": "ALLOW_PONDING", "description": "YES or NO", "type": "str"},
            {"name": "SKIP_STEADY_STATE", "description": "YES or NO", "type": "str"},
            {"name": "START_DATE", "description": "Simulation start date", "unit": "MM/DD/YYYY"},
            {"name": "END_DATE", "description": "Simulation end date", "unit": "MM/DD/YYYY"},
            {"name": "REPORT_STEP", "description": "Reporting time step", "unit": "HH:MM:SS"},
            {"name": "WET_STEP", "description": "Routing time step during wet weather", "unit": "HH:MM:SS"},
            {"name": "DRY_STEP", "description": "Routing time step during dry weather", "unit": "HH:MM:SS"},
        ],
        "example": "FLOW_UNITS  CFS\nINFILTRATION  GREEN_AMPT\nFLOW_ROUTING  DYNWAVE",
        "keywords": ["options", "flow units", "routing", "kinematic", "dynamic wave", "steady", "time step", "simulation"],
    },
    "TREATMENT": {
        "description": "Pollutant treatment expressions at nodes",
        "fields": [
            {"name": "Node", "description": "Node name", "type": "str"},
            {"name": "Pollutant", "description": "Pollutant name", "type": "str"},
            {"name": "Function", "description": "Treatment function (R = removal, C = concentration)", "type": "expression"},
        ],
        "example": "J1  TSS  R = 0.75 * HRT / (0.5 + HRT)",
        "keywords": ["treatment", "removal", "concentration", "BMP", "HRT", "detention time", "water quality"],
    },
}


def find_matching_inp_sections(query):
    if not query or not query.strip():
        return []
    q_lower = query.lower()
    terms = [t.strip().lower() for t in q_lower.split(',') if t.strip()]

    scored = []
    for section_name, section_data in INP_SECTIONS.items():
        score = 0
        keywords = section_data.get("keywords", [])
        for term in terms:
            if term in section_name.lower():
                score += 10
            for kw in keywords:
                if term in kw or kw in term:
                    score += 5
                elif any(w in kw for w in term.split()):
                    score += 2
            desc = section_data.get("description", "").lower()
            if term in desc:
                score += 3

        if score > 0:
            result = {
                "section": section_name,
                "description": section_data["description"],
                "example": section_data.get("example", ""),
                "score": score,
            }
            if "fields" in section_data:
                result["fields"] = section_data["fields"]
            if "methods" in section_data:
                best_method = None
                best_score = 0
                for method_name, method_data in section_data["methods"].items():
                    mscore = 0
                    for term in terms:
                        if term in method_name.lower():
                            mscore += 10
                    if mscore > best_score:
                        best_score = mscore
                        best_method = method_name
                if best_method:
                    m = section_data["methods"][best_method]
                    result["fields"] = m["fields"]
                    result["example"] = m.get("example", "")
                    result["method"] = best_method
                else:
                    first_method = list(section_data["methods"].keys())[0]
                    m = section_data["methods"][first_method]
                    result["fields"] = m["fields"]
                    result["example"] = m.get("example", "")
                    result["method"] = first_method
                    result["all_methods"] = list(section_data["methods"].keys())
            if "layers" in section_data:
                result["layers"] = section_data["layers"]
            scored.append(result)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:3]