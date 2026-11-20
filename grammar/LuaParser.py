# Generated from LuaParser.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

if "." in __name__:
    from .LuaParserBase import LuaParserBase
else:
    from LuaParserBase import LuaParserBase

def serializedATN():
    return [
        4,1,67,426,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,1,0,1,0,1,
        0,1,1,1,1,1,2,5,2,59,8,2,10,2,12,2,62,9,2,1,2,3,2,65,8,2,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        5,3,101,8,3,10,3,12,3,104,9,3,1,3,1,3,3,3,108,8,3,1,3,1,3,1,3,1,
        3,1,3,1,3,1,3,1,3,1,3,1,3,3,3,120,8,3,1,3,1,3,1,3,1,3,1,3,1,3,1,
        3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,
        3,1,3,3,3,146,8,3,3,3,148,8,3,1,4,1,4,1,4,1,4,1,4,5,4,155,8,4,10,
        4,12,4,158,9,4,1,5,1,5,1,5,3,5,163,8,5,1,6,1,6,3,6,167,8,6,1,6,3,
        6,170,8,6,1,7,1,7,1,7,1,7,1,8,1,8,1,8,5,8,179,8,8,10,8,12,8,182,
        9,8,1,8,1,8,3,8,186,8,8,1,9,1,9,1,9,5,9,191,8,9,10,9,12,9,194,9,
        9,1,10,1,10,1,10,5,10,199,8,10,10,10,12,10,202,9,10,1,11,1,11,1,
        11,5,11,207,8,11,10,11,12,11,210,9,11,1,12,1,12,1,12,1,12,1,12,1,
        12,1,12,1,12,1,12,1,12,1,12,1,12,3,12,224,8,12,1,12,1,12,1,12,1,
        12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,
        12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,
        12,1,12,1,12,1,12,5,12,259,8,12,10,12,12,12,262,9,12,1,13,1,13,1,
        13,1,13,1,13,1,13,1,13,1,13,3,13,272,8,13,3,13,274,8,13,1,14,1,14,
        1,14,1,14,1,14,1,14,1,14,1,14,5,14,284,8,14,10,14,12,14,287,9,14,
        1,14,1,14,1,14,1,14,1,14,1,14,1,14,5,14,296,8,14,10,14,12,14,299,
        9,14,1,14,1,14,1,14,1,14,1,14,1,14,1,14,1,14,1,14,5,14,310,8,14,
        10,14,12,14,313,9,14,3,14,315,8,14,1,15,1,15,1,15,1,15,1,15,3,15,
        322,8,15,1,15,1,15,1,15,1,15,1,15,1,15,5,15,330,8,15,10,15,12,15,
        333,9,15,1,15,1,15,1,15,1,15,3,15,339,8,15,1,15,1,15,1,15,1,15,1,
        15,1,15,5,15,347,8,15,10,15,12,15,350,9,15,1,15,1,15,1,15,1,15,3,
        15,356,8,15,5,15,358,8,15,10,15,12,15,361,9,15,1,16,1,16,3,16,365,
        8,16,1,16,1,16,1,16,3,16,370,8,16,1,17,1,17,1,17,1,18,1,18,1,18,
        1,18,1,18,1,18,1,19,1,19,1,19,3,19,384,8,19,1,19,1,19,3,19,388,8,
        19,1,20,1,20,3,20,392,8,20,1,20,1,20,1,21,1,21,1,21,1,21,5,21,400,
        8,21,10,21,12,21,403,9,21,1,21,3,21,406,8,21,1,22,1,22,1,22,1,22,
        1,22,1,22,1,22,1,22,1,22,1,22,3,22,418,8,22,1,23,1,23,1,24,1,24,
        1,25,1,25,1,25,0,1,24,26,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,
        30,32,34,36,38,40,42,44,46,48,50,0,8,2,0,27,29,32,32,3,0,36,37,44,
        44,53,53,2,0,28,28,43,43,1,0,33,34,4,0,19,20,39,40,49,49,55,55,2,
        0,1,1,15,15,1,0,60,63,1,0,57,59,477,0,52,1,0,0,0,2,55,1,0,0,0,4,
        60,1,0,0,0,6,147,1,0,0,0,8,149,1,0,0,0,10,162,1,0,0,0,12,164,1,0,
        0,0,14,171,1,0,0,0,16,175,1,0,0,0,18,187,1,0,0,0,20,195,1,0,0,0,
        22,203,1,0,0,0,24,223,1,0,0,0,26,273,1,0,0,0,28,314,1,0,0,0,30,321,
        1,0,0,0,32,369,1,0,0,0,34,371,1,0,0,0,36,374,1,0,0,0,38,387,1,0,
        0,0,40,389,1,0,0,0,42,395,1,0,0,0,44,417,1,0,0,0,46,419,1,0,0,0,
        48,421,1,0,0,0,50,423,1,0,0,0,52,53,3,2,1,0,53,54,5,0,0,1,54,1,1,
        0,0,0,55,56,3,4,2,0,56,3,1,0,0,0,57,59,3,6,3,0,58,57,1,0,0,0,59,
        62,1,0,0,0,60,58,1,0,0,0,60,61,1,0,0,0,61,64,1,0,0,0,62,60,1,0,0,
        0,63,65,3,12,6,0,64,63,1,0,0,0,64,65,1,0,0,0,65,5,1,0,0,0,66,148,
        5,1,0,0,67,68,3,18,9,0,68,69,5,2,0,0,69,70,3,22,11,0,70,148,1,0,
        0,0,71,148,3,30,15,0,72,148,3,14,7,0,73,148,5,3,0,0,74,75,5,4,0,
        0,75,148,5,56,0,0,76,77,5,5,0,0,77,78,3,4,2,0,78,79,5,6,0,0,79,148,
        1,0,0,0,80,81,5,7,0,0,81,82,3,24,12,0,82,83,5,5,0,0,83,84,3,4,2,
        0,84,85,5,6,0,0,85,148,1,0,0,0,86,87,5,8,0,0,87,88,3,4,2,0,88,89,
        5,9,0,0,89,90,3,24,12,0,90,148,1,0,0,0,91,92,5,10,0,0,92,93,3,24,
        12,0,93,94,5,11,0,0,94,102,3,4,2,0,95,96,5,12,0,0,96,97,3,24,12,
        0,97,98,5,11,0,0,98,99,3,4,2,0,99,101,1,0,0,0,100,95,1,0,0,0,101,
        104,1,0,0,0,102,100,1,0,0,0,102,103,1,0,0,0,103,107,1,0,0,0,104,
        102,1,0,0,0,105,106,5,13,0,0,106,108,3,4,2,0,107,105,1,0,0,0,107,
        108,1,0,0,0,108,109,1,0,0,0,109,110,5,6,0,0,110,148,1,0,0,0,111,
        112,5,14,0,0,112,113,5,56,0,0,113,114,5,2,0,0,114,115,3,24,12,0,
        115,116,5,15,0,0,116,119,3,24,12,0,117,118,5,15,0,0,118,120,3,24,
        12,0,119,117,1,0,0,0,119,120,1,0,0,0,120,121,1,0,0,0,121,122,5,5,
        0,0,122,123,3,4,2,0,123,124,5,6,0,0,124,148,1,0,0,0,125,126,5,14,
        0,0,126,127,3,20,10,0,127,128,5,16,0,0,128,129,3,22,11,0,129,130,
        5,5,0,0,130,131,3,4,2,0,131,132,5,6,0,0,132,148,1,0,0,0,133,134,
        5,17,0,0,134,135,3,16,8,0,135,136,3,36,18,0,136,148,1,0,0,0,137,
        138,5,18,0,0,138,139,5,17,0,0,139,140,5,56,0,0,140,148,3,36,18,0,
        141,142,5,18,0,0,142,145,3,8,4,0,143,144,5,2,0,0,144,146,3,22,11,
        0,145,143,1,0,0,0,145,146,1,0,0,0,146,148,1,0,0,0,147,66,1,0,0,0,
        147,67,1,0,0,0,147,71,1,0,0,0,147,72,1,0,0,0,147,73,1,0,0,0,147,
        74,1,0,0,0,147,76,1,0,0,0,147,80,1,0,0,0,147,86,1,0,0,0,147,91,1,
        0,0,0,147,111,1,0,0,0,147,125,1,0,0,0,147,133,1,0,0,0,147,137,1,
        0,0,0,147,141,1,0,0,0,148,7,1,0,0,0,149,150,5,56,0,0,150,156,3,10,
        5,0,151,152,5,15,0,0,152,153,5,56,0,0,153,155,3,10,5,0,154,151,1,
        0,0,0,155,158,1,0,0,0,156,154,1,0,0,0,156,157,1,0,0,0,157,9,1,0,
        0,0,158,156,1,0,0,0,159,160,5,19,0,0,160,161,5,56,0,0,161,163,5,
        20,0,0,162,159,1,0,0,0,162,163,1,0,0,0,163,11,1,0,0,0,164,166,5,
        21,0,0,165,167,3,22,11,0,166,165,1,0,0,0,166,167,1,0,0,0,167,169,
        1,0,0,0,168,170,5,1,0,0,169,168,1,0,0,0,169,170,1,0,0,0,170,13,1,
        0,0,0,171,172,5,22,0,0,172,173,5,56,0,0,173,174,5,22,0,0,174,15,
        1,0,0,0,175,180,5,56,0,0,176,177,5,26,0,0,177,179,5,56,0,0,178,176,
        1,0,0,0,179,182,1,0,0,0,180,178,1,0,0,0,180,181,1,0,0,0,181,185,
        1,0,0,0,182,180,1,0,0,0,183,184,5,38,0,0,184,186,5,56,0,0,185,183,
        1,0,0,0,185,186,1,0,0,0,186,17,1,0,0,0,187,192,3,26,13,0,188,189,
        5,15,0,0,189,191,3,26,13,0,190,188,1,0,0,0,191,194,1,0,0,0,192,190,
        1,0,0,0,192,193,1,0,0,0,193,19,1,0,0,0,194,192,1,0,0,0,195,200,5,
        56,0,0,196,197,5,15,0,0,197,199,5,56,0,0,198,196,1,0,0,0,199,202,
        1,0,0,0,200,198,1,0,0,0,200,201,1,0,0,0,201,21,1,0,0,0,202,200,1,
        0,0,0,203,208,3,24,12,0,204,205,5,15,0,0,205,207,3,24,12,0,206,204,
        1,0,0,0,207,210,1,0,0,0,208,206,1,0,0,0,208,209,1,0,0,0,209,23,1,
        0,0,0,210,208,1,0,0,0,211,212,6,12,-1,0,212,224,5,23,0,0,213,224,
        5,24,0,0,214,224,5,25,0,0,215,224,3,48,24,0,216,224,3,50,25,0,217,
        224,5,54,0,0,218,224,3,34,17,0,219,224,3,28,14,0,220,224,3,40,20,
        0,221,222,7,0,0,0,222,224,3,24,12,11,223,211,1,0,0,0,223,213,1,0,
        0,0,223,214,1,0,0,0,223,215,1,0,0,0,223,216,1,0,0,0,223,217,1,0,
        0,0,223,218,1,0,0,0,223,219,1,0,0,0,223,220,1,0,0,0,223,221,1,0,
        0,0,224,260,1,0,0,0,225,226,10,12,0,0,226,227,5,52,0,0,227,259,3,
        24,12,12,228,229,10,10,0,0,229,230,7,1,0,0,230,259,3,24,12,11,231,
        232,10,9,0,0,232,233,7,2,0,0,233,259,3,24,12,10,234,235,10,8,0,0,
        235,236,5,50,0,0,236,259,3,24,12,8,237,238,10,7,0,0,238,239,7,3,
        0,0,239,259,3,24,12,8,240,241,10,6,0,0,241,242,5,35,0,0,242,259,
        3,24,12,7,243,244,10,5,0,0,244,245,5,27,0,0,245,259,3,24,12,6,246,
        247,10,4,0,0,247,248,5,51,0,0,248,259,3,24,12,5,249,250,10,3,0,0,
        250,251,7,4,0,0,251,259,3,24,12,4,252,253,10,2,0,0,253,254,5,41,
        0,0,254,259,3,24,12,3,255,256,10,1,0,0,256,257,5,42,0,0,257,259,
        3,24,12,2,258,225,1,0,0,0,258,228,1,0,0,0,258,231,1,0,0,0,258,234,
        1,0,0,0,258,237,1,0,0,0,258,240,1,0,0,0,258,243,1,0,0,0,258,246,
        1,0,0,0,258,249,1,0,0,0,258,252,1,0,0,0,258,255,1,0,0,0,259,262,
        1,0,0,0,260,258,1,0,0,0,260,261,1,0,0,0,261,25,1,0,0,0,262,260,1,
        0,0,0,263,274,5,56,0,0,264,271,3,28,14,0,265,266,5,47,0,0,266,267,
        3,24,12,0,267,268,5,48,0,0,268,272,1,0,0,0,269,270,5,26,0,0,270,
        272,5,56,0,0,271,265,1,0,0,0,271,269,1,0,0,0,272,274,1,0,0,0,273,
        263,1,0,0,0,273,264,1,0,0,0,274,27,1,0,0,0,275,276,4,14,11,0,276,
        285,5,56,0,0,277,278,5,47,0,0,278,279,3,24,12,0,279,280,5,48,0,0,
        280,284,1,0,0,0,281,282,5,26,0,0,282,284,5,56,0,0,283,277,1,0,0,
        0,283,281,1,0,0,0,284,287,1,0,0,0,285,283,1,0,0,0,285,286,1,0,0,
        0,286,315,1,0,0,0,287,285,1,0,0,0,288,297,3,30,15,0,289,290,5,47,
        0,0,290,291,3,24,12,0,291,292,5,48,0,0,292,296,1,0,0,0,293,294,5,
        26,0,0,294,296,5,56,0,0,295,289,1,0,0,0,295,293,1,0,0,0,296,299,
        1,0,0,0,297,295,1,0,0,0,297,298,1,0,0,0,298,315,1,0,0,0,299,297,
        1,0,0,0,300,301,5,30,0,0,301,302,3,24,12,0,302,311,5,31,0,0,303,
        304,5,47,0,0,304,305,3,24,12,0,305,306,5,48,0,0,306,310,1,0,0,0,
        307,308,5,26,0,0,308,310,5,56,0,0,309,303,1,0,0,0,309,307,1,0,0,
        0,310,313,1,0,0,0,311,309,1,0,0,0,311,312,1,0,0,0,312,315,1,0,0,
        0,313,311,1,0,0,0,314,275,1,0,0,0,314,288,1,0,0,0,314,300,1,0,0,
        0,315,29,1,0,0,0,316,322,5,56,0,0,317,318,5,30,0,0,318,319,3,24,
        12,0,319,320,5,31,0,0,320,322,1,0,0,0,321,316,1,0,0,0,321,317,1,
        0,0,0,322,331,1,0,0,0,323,324,5,47,0,0,324,325,3,24,12,0,325,326,
        5,48,0,0,326,330,1,0,0,0,327,328,5,26,0,0,328,330,5,56,0,0,329,323,
        1,0,0,0,329,327,1,0,0,0,330,333,1,0,0,0,331,329,1,0,0,0,331,332,
        1,0,0,0,332,338,1,0,0,0,333,331,1,0,0,0,334,339,3,32,16,0,335,336,
        5,38,0,0,336,337,5,56,0,0,337,339,3,32,16,0,338,334,1,0,0,0,338,
        335,1,0,0,0,339,359,1,0,0,0,340,341,5,47,0,0,341,342,3,24,12,0,342,
        343,5,48,0,0,343,347,1,0,0,0,344,345,5,26,0,0,345,347,5,56,0,0,346,
        340,1,0,0,0,346,344,1,0,0,0,347,350,1,0,0,0,348,346,1,0,0,0,348,
        349,1,0,0,0,349,355,1,0,0,0,350,348,1,0,0,0,351,356,3,32,16,0,352,
        353,5,38,0,0,353,354,5,56,0,0,354,356,3,32,16,0,355,351,1,0,0,0,
        355,352,1,0,0,0,356,358,1,0,0,0,357,348,1,0,0,0,358,361,1,0,0,0,
        359,357,1,0,0,0,359,360,1,0,0,0,360,31,1,0,0,0,361,359,1,0,0,0,362,
        364,5,30,0,0,363,365,3,22,11,0,364,363,1,0,0,0,364,365,1,0,0,0,365,
        366,1,0,0,0,366,370,5,31,0,0,367,370,3,40,20,0,368,370,3,50,25,0,
        369,362,1,0,0,0,369,367,1,0,0,0,369,368,1,0,0,0,370,33,1,0,0,0,371,
        372,5,17,0,0,372,373,3,36,18,0,373,35,1,0,0,0,374,375,5,30,0,0,375,
        376,3,38,19,0,376,377,5,31,0,0,377,378,3,4,2,0,378,379,5,6,0,0,379,
        37,1,0,0,0,380,383,3,20,10,0,381,382,5,15,0,0,382,384,5,54,0,0,383,
        381,1,0,0,0,383,384,1,0,0,0,384,388,1,0,0,0,385,388,5,54,0,0,386,
        388,1,0,0,0,387,380,1,0,0,0,387,385,1,0,0,0,387,386,1,0,0,0,388,
        39,1,0,0,0,389,391,5,45,0,0,390,392,3,42,21,0,391,390,1,0,0,0,391,
        392,1,0,0,0,392,393,1,0,0,0,393,394,5,46,0,0,394,41,1,0,0,0,395,
        401,3,44,22,0,396,397,3,46,23,0,397,398,3,44,22,0,398,400,1,0,0,
        0,399,396,1,0,0,0,400,403,1,0,0,0,401,399,1,0,0,0,401,402,1,0,0,
        0,402,405,1,0,0,0,403,401,1,0,0,0,404,406,3,46,23,0,405,404,1,0,
        0,0,405,406,1,0,0,0,406,43,1,0,0,0,407,408,5,47,0,0,408,409,3,24,
        12,0,409,410,5,48,0,0,410,411,5,2,0,0,411,412,3,24,12,0,412,418,
        1,0,0,0,413,414,5,56,0,0,414,415,5,2,0,0,415,418,3,24,12,0,416,418,
        3,24,12,0,417,407,1,0,0,0,417,413,1,0,0,0,417,416,1,0,0,0,418,45,
        1,0,0,0,419,420,7,5,0,0,420,47,1,0,0,0,421,422,7,6,0,0,422,49,1,
        0,0,0,423,424,7,7,0,0,424,51,1,0,0,0,44,60,64,102,107,119,145,147,
        156,162,166,169,180,185,192,200,208,223,258,260,271,273,283,285,
        295,297,309,311,314,321,329,331,338,346,348,355,359,364,369,383,
        387,391,401,405,417
    ]

class LuaParser ( LuaParserBase ):

    grammarFileName = "LuaParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "';'", "'='", "'break'", "'goto'", "'do'", 
                     "'end'", "'while'", "'repeat'", "'until'", "'if'", 
                     "'then'", "'elseif'", "'else'", "'for'", "','", "'in'", 
                     "'function'", "'local'", "'<'", "'>'", "'return'", 
                     "'::'", "'nil'", "'false'", "'true'", "'.'", "'~'", 
                     "'-'", "'#'", "'('", "')'", "'not'", "'<<'", "'>>'", 
                     "'&'", "'//'", "'%'", "':'", "'<='", "'>='", "'and'", 
                     "'or'", "'+'", "'*'", "'{'", "'}'", "'['", "']'", "'=='", 
                     "'..'", "'|'", "'^'", "'/'", "'...'", "'~='" ]

    symbolicNames = [ "<INVALID>", "SEMI", "EQ", "BREAK", "GOTO", "DO", 
                      "END", "WHILE", "REPEAT", "UNTIL", "IF", "THEN", "ELSEIF", 
                      "ELSE", "FOR", "COMMA", "IN", "FUNCTION", "LOCAL", 
                      "LT", "GT", "RETURN", "CC", "NIL", "FALSE", "TRUE", 
                      "DOT", "SQUIG", "MINUS", "POUND", "OP", "CP", "NOT", 
                      "LL", "GG", "AMP", "SS", "PER", "COL", "LE", "GE", 
                      "AND", "OR", "PLUS", "STAR", "OCU", "CCU", "OB", "CB", 
                      "EE", "DD", "PIPE", "CARET", "SLASH", "DDD", "SQEQ", 
                      "NAME", "NORMALSTRING", "CHARSTRING", "LONGSTRING", 
                      "INT", "HEX", "FLOAT", "HEX_FLOAT", "COMMENT", "WS", 
                      "NL", "SHEBANG" ]

    RULE_start_ = 0
    RULE_chunk = 1
    RULE_block = 2
    RULE_stat = 3
    RULE_attnamelist = 4
    RULE_attrib = 5
    RULE_retstat = 6
    RULE_label = 7
    RULE_funcname = 8
    RULE_varlist = 9
    RULE_namelist = 10
    RULE_explist = 11
    RULE_exp = 12
    RULE_var = 13
    RULE_prefixexp = 14
    RULE_functioncall = 15
    RULE_args = 16
    RULE_functiondef = 17
    RULE_funcbody = 18
    RULE_parlist = 19
    RULE_tableconstructor = 20
    RULE_fieldlist = 21
    RULE_field = 22
    RULE_fieldsep = 23
    RULE_number = 24
    RULE_string = 25

    ruleNames =  [ "start_", "chunk", "block", "stat", "attnamelist", "attrib", 
                   "retstat", "label", "funcname", "varlist", "namelist", 
                   "explist", "exp", "var", "prefixexp", "functioncall", 
                   "args", "functiondef", "funcbody", "parlist", "tableconstructor", 
                   "fieldlist", "field", "fieldsep", "number", "string" ]

    EOF = Token.EOF
    SEMI=1
    EQ=2
    BREAK=3
    GOTO=4
    DO=5
    END=6
    WHILE=7
    REPEAT=8
    UNTIL=9
    IF=10
    THEN=11
    ELSEIF=12
    ELSE=13
    FOR=14
    COMMA=15
    IN=16
    FUNCTION=17
    LOCAL=18
    LT=19
    GT=20
    RETURN=21
    CC=22
    NIL=23
    FALSE=24
    TRUE=25
    DOT=26
    SQUIG=27
    MINUS=28
    POUND=29
    OP=30
    CP=31
    NOT=32
    LL=33
    GG=34
    AMP=35
    SS=36
    PER=37
    COL=38
    LE=39
    GE=40
    AND=41
    OR=42
    PLUS=43
    STAR=44
    OCU=45
    CCU=46
    OB=47
    CB=48
    EE=49
    DD=50
    PIPE=51
    CARET=52
    SLASH=53
    DDD=54
    SQEQ=55
    NAME=56
    NORMALSTRING=57
    CHARSTRING=58
    LONGSTRING=59
    INT=60
    HEX=61
    FLOAT=62
    HEX_FLOAT=63
    COMMENT=64
    WS=65
    NL=66
    SHEBANG=67

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Start_Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def chunk(self):
            return self.getTypedRuleContext(LuaParser.ChunkContext,0)


        def EOF(self):
            return self.getToken(LuaParser.EOF, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_start_

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStart_" ):
                return visitor.visitStart_(self)
            else:
                return visitor.visitChildren(self)




    def start_(self):

        localctx = LuaParser.Start_Context(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_start_)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 52
            self.chunk()
            self.state = 53
            self.match(LuaParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ChunkContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def block(self):
            return self.getTypedRuleContext(LuaParser.BlockContext,0)


        def getRuleIndex(self):
            return LuaParser.RULE_chunk

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitChunk" ):
                return visitor.visitChunk(self)
            else:
                return visitor.visitChildren(self)




    def chunk(self):

        localctx = LuaParser.ChunkContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_chunk)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 55
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def stat(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LuaParser.StatContext)
            else:
                return self.getTypedRuleContext(LuaParser.StatContext,i)


        def retstat(self):
            return self.getTypedRuleContext(LuaParser.RetstatContext,0)


        def getRuleIndex(self):
            return LuaParser.RULE_block

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBlock" ):
                return visitor.visitBlock(self)
            else:
                return visitor.visitChildren(self)




    def block(self):

        localctx = LuaParser.BlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 60
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,0,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 57
                    self.stat() 
                self.state = 62
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,0,self._ctx)

            self.state = 64
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==21:
                self.state = 63
                self.retstat()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SEMI(self):
            return self.getToken(LuaParser.SEMI, 0)

        def varlist(self):
            return self.getTypedRuleContext(LuaParser.VarlistContext,0)


        def EQ(self):
            return self.getToken(LuaParser.EQ, 0)

        def explist(self):
            return self.getTypedRuleContext(LuaParser.ExplistContext,0)


        def functioncall(self):
            return self.getTypedRuleContext(LuaParser.FunctioncallContext,0)


        def label(self):
            return self.getTypedRuleContext(LuaParser.LabelContext,0)


        def BREAK(self):
            return self.getToken(LuaParser.BREAK, 0)

        def GOTO(self):
            return self.getToken(LuaParser.GOTO, 0)

        def NAME(self):
            return self.getToken(LuaParser.NAME, 0)

        def DO(self):
            return self.getToken(LuaParser.DO, 0)

        def block(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LuaParser.BlockContext)
            else:
                return self.getTypedRuleContext(LuaParser.BlockContext,i)


        def END(self):
            return self.getToken(LuaParser.END, 0)

        def WHILE(self):
            return self.getToken(LuaParser.WHILE, 0)

        def exp(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LuaParser.ExpContext)
            else:
                return self.getTypedRuleContext(LuaParser.ExpContext,i)


        def REPEAT(self):
            return self.getToken(LuaParser.REPEAT, 0)

        def UNTIL(self):
            return self.getToken(LuaParser.UNTIL, 0)

        def IF(self):
            return self.getToken(LuaParser.IF, 0)

        def THEN(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.THEN)
            else:
                return self.getToken(LuaParser.THEN, i)

        def ELSEIF(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.ELSEIF)
            else:
                return self.getToken(LuaParser.ELSEIF, i)

        def ELSE(self):
            return self.getToken(LuaParser.ELSE, 0)

        def FOR(self):
            return self.getToken(LuaParser.FOR, 0)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.COMMA)
            else:
                return self.getToken(LuaParser.COMMA, i)

        def namelist(self):
            return self.getTypedRuleContext(LuaParser.NamelistContext,0)


        def IN(self):
            return self.getToken(LuaParser.IN, 0)

        def FUNCTION(self):
            return self.getToken(LuaParser.FUNCTION, 0)

        def funcname(self):
            return self.getTypedRuleContext(LuaParser.FuncnameContext,0)


        def funcbody(self):
            return self.getTypedRuleContext(LuaParser.FuncbodyContext,0)


        def LOCAL(self):
            return self.getToken(LuaParser.LOCAL, 0)

        def attnamelist(self):
            return self.getTypedRuleContext(LuaParser.AttnamelistContext,0)


        def getRuleIndex(self):
            return LuaParser.RULE_stat

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStat" ):
                return visitor.visitStat(self)
            else:
                return visitor.visitChildren(self)




    def stat(self):

        localctx = LuaParser.StatContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_stat)
        self._la = 0 # Token type
        try:
            self.state = 147
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,6,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 66
                self.match(LuaParser.SEMI)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 67
                self.varlist()
                self.state = 68
                self.match(LuaParser.EQ)
                self.state = 69
                self.explist()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 71
                self.functioncall()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 72
                self.label()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 73
                self.match(LuaParser.BREAK)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 74
                self.match(LuaParser.GOTO)
                self.state = 75
                self.match(LuaParser.NAME)
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 76
                self.match(LuaParser.DO)
                self.state = 77
                self.block()
                self.state = 78
                self.match(LuaParser.END)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 80
                self.match(LuaParser.WHILE)
                self.state = 81
                self.exp(0)
                self.state = 82
                self.match(LuaParser.DO)
                self.state = 83
                self.block()
                self.state = 84
                self.match(LuaParser.END)
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 86
                self.match(LuaParser.REPEAT)
                self.state = 87
                self.block()
                self.state = 88
                self.match(LuaParser.UNTIL)
                self.state = 89
                self.exp(0)
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 91
                self.match(LuaParser.IF)
                self.state = 92
                self.exp(0)
                self.state = 93
                self.match(LuaParser.THEN)
                self.state = 94
                self.block()
                self.state = 102
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 95
                    self.match(LuaParser.ELSEIF)
                    self.state = 96
                    self.exp(0)
                    self.state = 97
                    self.match(LuaParser.THEN)
                    self.state = 98
                    self.block()
                    self.state = 104
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 107
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==13:
                    self.state = 105
                    self.match(LuaParser.ELSE)
                    self.state = 106
                    self.block()


                self.state = 109
                self.match(LuaParser.END)
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 111
                self.match(LuaParser.FOR)
                self.state = 112
                self.match(LuaParser.NAME)
                self.state = 113
                self.match(LuaParser.EQ)
                self.state = 114
                self.exp(0)
                self.state = 115
                self.match(LuaParser.COMMA)
                self.state = 116
                self.exp(0)
                self.state = 119
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==15:
                    self.state = 117
                    self.match(LuaParser.COMMA)
                    self.state = 118
                    self.exp(0)


                self.state = 121
                self.match(LuaParser.DO)
                self.state = 122
                self.block()
                self.state = 123
                self.match(LuaParser.END)
                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 125
                self.match(LuaParser.FOR)
                self.state = 126
                self.namelist()
                self.state = 127
                self.match(LuaParser.IN)
                self.state = 128
                self.explist()
                self.state = 129
                self.match(LuaParser.DO)
                self.state = 130
                self.block()
                self.state = 131
                self.match(LuaParser.END)
                pass

            elif la_ == 13:
                self.enterOuterAlt(localctx, 13)
                self.state = 133
                self.match(LuaParser.FUNCTION)
                self.state = 134
                self.funcname()
                self.state = 135
                self.funcbody()
                pass

            elif la_ == 14:
                self.enterOuterAlt(localctx, 14)
                self.state = 137
                self.match(LuaParser.LOCAL)
                self.state = 138
                self.match(LuaParser.FUNCTION)
                self.state = 139
                self.match(LuaParser.NAME)
                self.state = 140
                self.funcbody()
                pass

            elif la_ == 15:
                self.enterOuterAlt(localctx, 15)
                self.state = 141
                self.match(LuaParser.LOCAL)
                self.state = 142
                self.attnamelist()
                self.state = 145
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
                if la_ == 1:
                    self.state = 143
                    self.match(LuaParser.EQ)
                    self.state = 144
                    self.explist()


                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AttnamelistContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.NAME)
            else:
                return self.getToken(LuaParser.NAME, i)

        def attrib(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LuaParser.AttribContext)
            else:
                return self.getTypedRuleContext(LuaParser.AttribContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.COMMA)
            else:
                return self.getToken(LuaParser.COMMA, i)

        def getRuleIndex(self):
            return LuaParser.RULE_attnamelist

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAttnamelist" ):
                return visitor.visitAttnamelist(self)
            else:
                return visitor.visitChildren(self)




    def attnamelist(self):

        localctx = LuaParser.AttnamelistContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_attnamelist)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 149
            self.match(LuaParser.NAME)
            self.state = 150
            self.attrib()
            self.state = 156
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,7,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 151
                    self.match(LuaParser.COMMA)
                    self.state = 152
                    self.match(LuaParser.NAME)
                    self.state = 153
                    self.attrib() 
                self.state = 158
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,7,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AttribContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LT(self):
            return self.getToken(LuaParser.LT, 0)

        def NAME(self):
            return self.getToken(LuaParser.NAME, 0)

        def GT(self):
            return self.getToken(LuaParser.GT, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_attrib

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAttrib" ):
                return visitor.visitAttrib(self)
            else:
                return visitor.visitChildren(self)




    def attrib(self):

        localctx = LuaParser.AttribContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_attrib)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 162
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,8,self._ctx)
            if la_ == 1:
                self.state = 159
                self.match(LuaParser.LT)
                self.state = 160
                self.match(LuaParser.NAME)
                self.state = 161
                self.match(LuaParser.GT)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RetstatContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN(self):
            return self.getToken(LuaParser.RETURN, 0)

        def explist(self):
            return self.getTypedRuleContext(LuaParser.ExplistContext,0)


        def SEMI(self):
            return self.getToken(LuaParser.SEMI, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_retstat

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRetstat" ):
                return visitor.visitRetstat(self)
            else:
                return visitor.visitChildren(self)




    def retstat(self):

        localctx = LuaParser.RetstatContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_retstat)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 164
            self.match(LuaParser.RETURN)
            self.state = 166
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,9,self._ctx)
            if la_ == 1:
                self.state = 165
                self.explist()


            self.state = 169
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 168
                self.match(LuaParser.SEMI)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LabelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CC(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.CC)
            else:
                return self.getToken(LuaParser.CC, i)

        def NAME(self):
            return self.getToken(LuaParser.NAME, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_label

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLabel" ):
                return visitor.visitLabel(self)
            else:
                return visitor.visitChildren(self)




    def label(self):

        localctx = LuaParser.LabelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_label)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 171
            self.match(LuaParser.CC)
            self.state = 172
            self.match(LuaParser.NAME)
            self.state = 173
            self.match(LuaParser.CC)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FuncnameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.NAME)
            else:
                return self.getToken(LuaParser.NAME, i)

        def DOT(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.DOT)
            else:
                return self.getToken(LuaParser.DOT, i)

        def COL(self):
            return self.getToken(LuaParser.COL, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_funcname

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFuncname" ):
                return visitor.visitFuncname(self)
            else:
                return visitor.visitChildren(self)




    def funcname(self):

        localctx = LuaParser.FuncnameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_funcname)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 175
            self.match(LuaParser.NAME)
            self.state = 180
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==26:
                self.state = 176
                self.match(LuaParser.DOT)
                self.state = 177
                self.match(LuaParser.NAME)
                self.state = 182
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 185
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==38:
                self.state = 183
                self.match(LuaParser.COL)
                self.state = 184
                self.match(LuaParser.NAME)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VarlistContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def var(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LuaParser.VarContext)
            else:
                return self.getTypedRuleContext(LuaParser.VarContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.COMMA)
            else:
                return self.getToken(LuaParser.COMMA, i)

        def getRuleIndex(self):
            return LuaParser.RULE_varlist

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVarlist" ):
                return visitor.visitVarlist(self)
            else:
                return visitor.visitChildren(self)




    def varlist(self):

        localctx = LuaParser.VarlistContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_varlist)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 187
            self.var()
            self.state = 192
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==15:
                self.state = 188
                self.match(LuaParser.COMMA)
                self.state = 189
                self.var()
                self.state = 194
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NamelistContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.NAME)
            else:
                return self.getToken(LuaParser.NAME, i)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.COMMA)
            else:
                return self.getToken(LuaParser.COMMA, i)

        def getRuleIndex(self):
            return LuaParser.RULE_namelist

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNamelist" ):
                return visitor.visitNamelist(self)
            else:
                return visitor.visitChildren(self)




    def namelist(self):

        localctx = LuaParser.NamelistContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_namelist)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 195
            self.match(LuaParser.NAME)
            self.state = 200
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,14,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 196
                    self.match(LuaParser.COMMA)
                    self.state = 197
                    self.match(LuaParser.NAME) 
                self.state = 202
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,14,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExplistContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def exp(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LuaParser.ExpContext)
            else:
                return self.getTypedRuleContext(LuaParser.ExpContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.COMMA)
            else:
                return self.getToken(LuaParser.COMMA, i)

        def getRuleIndex(self):
            return LuaParser.RULE_explist

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExplist" ):
                return visitor.visitExplist(self)
            else:
                return visitor.visitChildren(self)




    def explist(self):

        localctx = LuaParser.ExplistContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_explist)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 203
            self.exp(0)
            self.state = 208
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,15,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 204
                    self.match(LuaParser.COMMA)
                    self.state = 205
                    self.exp(0) 
                self.state = 210
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,15,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NIL(self):
            return self.getToken(LuaParser.NIL, 0)

        def FALSE(self):
            return self.getToken(LuaParser.FALSE, 0)

        def TRUE(self):
            return self.getToken(LuaParser.TRUE, 0)

        def number(self):
            return self.getTypedRuleContext(LuaParser.NumberContext,0)


        def string(self):
            return self.getTypedRuleContext(LuaParser.StringContext,0)


        def DDD(self):
            return self.getToken(LuaParser.DDD, 0)

        def functiondef(self):
            return self.getTypedRuleContext(LuaParser.FunctiondefContext,0)


        def prefixexp(self):
            return self.getTypedRuleContext(LuaParser.PrefixexpContext,0)


        def tableconstructor(self):
            return self.getTypedRuleContext(LuaParser.TableconstructorContext,0)


        def exp(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LuaParser.ExpContext)
            else:
                return self.getTypedRuleContext(LuaParser.ExpContext,i)


        def NOT(self):
            return self.getToken(LuaParser.NOT, 0)

        def POUND(self):
            return self.getToken(LuaParser.POUND, 0)

        def MINUS(self):
            return self.getToken(LuaParser.MINUS, 0)

        def SQUIG(self):
            return self.getToken(LuaParser.SQUIG, 0)

        def CARET(self):
            return self.getToken(LuaParser.CARET, 0)

        def STAR(self):
            return self.getToken(LuaParser.STAR, 0)

        def SLASH(self):
            return self.getToken(LuaParser.SLASH, 0)

        def PER(self):
            return self.getToken(LuaParser.PER, 0)

        def SS(self):
            return self.getToken(LuaParser.SS, 0)

        def PLUS(self):
            return self.getToken(LuaParser.PLUS, 0)

        def DD(self):
            return self.getToken(LuaParser.DD, 0)

        def LL(self):
            return self.getToken(LuaParser.LL, 0)

        def GG(self):
            return self.getToken(LuaParser.GG, 0)

        def AMP(self):
            return self.getToken(LuaParser.AMP, 0)

        def PIPE(self):
            return self.getToken(LuaParser.PIPE, 0)

        def LT(self):
            return self.getToken(LuaParser.LT, 0)

        def GT(self):
            return self.getToken(LuaParser.GT, 0)

        def LE(self):
            return self.getToken(LuaParser.LE, 0)

        def GE(self):
            return self.getToken(LuaParser.GE, 0)

        def SQEQ(self):
            return self.getToken(LuaParser.SQEQ, 0)

        def EE(self):
            return self.getToken(LuaParser.EE, 0)

        def AND(self):
            return self.getToken(LuaParser.AND, 0)

        def OR(self):
            return self.getToken(LuaParser.OR, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_exp

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExp" ):
                return visitor.visitExp(self)
            else:
                return visitor.visitChildren(self)



    def exp(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = LuaParser.ExpContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 24
        self.enterRecursionRule(localctx, 24, self.RULE_exp, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 223
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,16,self._ctx)
            if la_ == 1:
                self.state = 212
                self.match(LuaParser.NIL)
                pass

            elif la_ == 2:
                self.state = 213
                self.match(LuaParser.FALSE)
                pass

            elif la_ == 3:
                self.state = 214
                self.match(LuaParser.TRUE)
                pass

            elif la_ == 4:
                self.state = 215
                self.number()
                pass

            elif la_ == 5:
                self.state = 216
                self.string()
                pass

            elif la_ == 6:
                self.state = 217
                self.match(LuaParser.DDD)
                pass

            elif la_ == 7:
                self.state = 218
                self.functiondef()
                pass

            elif la_ == 8:
                self.state = 219
                self.prefixexp()
                pass

            elif la_ == 9:
                self.state = 220
                self.tableconstructor()
                pass

            elif la_ == 10:
                self.state = 221
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 5234491392) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 222
                self.exp(11)
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 260
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,18,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 258
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,17,self._ctx)
                    if la_ == 1:
                        localctx = LuaParser.ExpContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_exp)
                        self.state = 225
                        if not self.precpred(self._ctx, 12):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 12)")

                        self.state = 226
                        self.match(LuaParser.CARET)
                        self.state = 227
                        self.exp(12)
                        pass

                    elif la_ == 2:
                        localctx = LuaParser.ExpContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_exp)
                        self.state = 228
                        if not self.precpred(self._ctx, 10):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 10)")
                        self.state = 229
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 9024997599215616) != 0)):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 230
                        self.exp(11)
                        pass

                    elif la_ == 3:
                        localctx = LuaParser.ExpContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_exp)
                        self.state = 231
                        if not self.precpred(self._ctx, 9):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 9)")
                        self.state = 232
                        _la = self._input.LA(1)
                        if not(_la==28 or _la==43):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 233
                        self.exp(10)
                        pass

                    elif la_ == 4:
                        localctx = LuaParser.ExpContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_exp)
                        self.state = 234
                        if not self.precpred(self._ctx, 8):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 8)")

                        self.state = 235
                        self.match(LuaParser.DD)
                        self.state = 236
                        self.exp(8)
                        pass

                    elif la_ == 5:
                        localctx = LuaParser.ExpContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_exp)
                        self.state = 237
                        if not self.precpred(self._ctx, 7):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 7)")
                        self.state = 238
                        _la = self._input.LA(1)
                        if not(_la==33 or _la==34):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 239
                        self.exp(8)
                        pass

                    elif la_ == 6:
                        localctx = LuaParser.ExpContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_exp)
                        self.state = 240
                        if not self.precpred(self._ctx, 6):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 6)")

                        self.state = 241
                        self.match(LuaParser.AMP)
                        self.state = 242
                        self.exp(7)
                        pass

                    elif la_ == 7:
                        localctx = LuaParser.ExpContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_exp)
                        self.state = 243
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")

                        self.state = 244
                        self.match(LuaParser.SQUIG)
                        self.state = 245
                        self.exp(6)
                        pass

                    elif la_ == 8:
                        localctx = LuaParser.ExpContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_exp)
                        self.state = 246
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")

                        self.state = 247
                        self.match(LuaParser.PIPE)
                        self.state = 248
                        self.exp(5)
                        pass

                    elif la_ == 9:
                        localctx = LuaParser.ExpContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_exp)
                        self.state = 249
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 250
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 36593396241399808) != 0)):
                            self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 251
                        self.exp(4)
                        pass

                    elif la_ == 10:
                        localctx = LuaParser.ExpContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_exp)
                        self.state = 252
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")

                        self.state = 253
                        self.match(LuaParser.AND)
                        self.state = 254
                        self.exp(3)
                        pass

                    elif la_ == 11:
                        localctx = LuaParser.ExpContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_exp)
                        self.state = 255
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")

                        self.state = 256
                        self.match(LuaParser.OR)
                        self.state = 257
                        self.exp(2)
                        pass

             
                self.state = 262
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,18,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class VarContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(LuaParser.NAME, 0)

        def prefixexp(self):
            return self.getTypedRuleContext(LuaParser.PrefixexpContext,0)


        def OB(self):
            return self.getToken(LuaParser.OB, 0)

        def exp(self):
            return self.getTypedRuleContext(LuaParser.ExpContext,0)


        def CB(self):
            return self.getToken(LuaParser.CB, 0)

        def DOT(self):
            return self.getToken(LuaParser.DOT, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_var

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVar" ):
                return visitor.visitVar(self)
            else:
                return visitor.visitChildren(self)




    def var(self):

        localctx = LuaParser.VarContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_var)
        try:
            self.state = 273
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,20,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 263
                self.match(LuaParser.NAME)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 264
                self.prefixexp()
                self.state = 271
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [47]:
                    self.state = 265
                    self.match(LuaParser.OB)
                    self.state = 266
                    self.exp(0)
                    self.state = 267
                    self.match(LuaParser.CB)
                    pass
                elif token in [26]:
                    self.state = 269
                    self.match(LuaParser.DOT)
                    self.state = 270
                    self.match(LuaParser.NAME)
                    pass
                else:
                    raise NoViableAltException(self)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PrefixexpContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.NAME)
            else:
                return self.getToken(LuaParser.NAME, i)

        def OB(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.OB)
            else:
                return self.getToken(LuaParser.OB, i)

        def exp(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LuaParser.ExpContext)
            else:
                return self.getTypedRuleContext(LuaParser.ExpContext,i)


        def CB(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.CB)
            else:
                return self.getToken(LuaParser.CB, i)

        def DOT(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.DOT)
            else:
                return self.getToken(LuaParser.DOT, i)

        def functioncall(self):
            return self.getTypedRuleContext(LuaParser.FunctioncallContext,0)


        def OP(self):
            return self.getToken(LuaParser.OP, 0)

        def CP(self):
            return self.getToken(LuaParser.CP, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_prefixexp

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrefixexp" ):
                return visitor.visitPrefixexp(self)
            else:
                return visitor.visitChildren(self)




    def prefixexp(self):

        localctx = LuaParser.PrefixexpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_prefixexp)
        try:
            self.state = 314
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,27,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 275
                if not  self.IsFunctionCall() :
                    from antlr4.error.Errors import FailedPredicateException
                    raise FailedPredicateException(self, " self.IsFunctionCall() ")
                self.state = 276
                self.match(LuaParser.NAME)
                self.state = 285
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,22,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 283
                        self._errHandler.sync(self)
                        token = self._input.LA(1)
                        if token in [47]:
                            self.state = 277
                            self.match(LuaParser.OB)
                            self.state = 278
                            self.exp(0)
                            self.state = 279
                            self.match(LuaParser.CB)
                            pass
                        elif token in [26]:
                            self.state = 281
                            self.match(LuaParser.DOT)
                            self.state = 282
                            self.match(LuaParser.NAME)
                            pass
                        else:
                            raise NoViableAltException(self)
                 
                    self.state = 287
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,22,self._ctx)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 288
                self.functioncall()
                self.state = 297
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,24,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 295
                        self._errHandler.sync(self)
                        token = self._input.LA(1)
                        if token in [47]:
                            self.state = 289
                            self.match(LuaParser.OB)
                            self.state = 290
                            self.exp(0)
                            self.state = 291
                            self.match(LuaParser.CB)
                            pass
                        elif token in [26]:
                            self.state = 293
                            self.match(LuaParser.DOT)
                            self.state = 294
                            self.match(LuaParser.NAME)
                            pass
                        else:
                            raise NoViableAltException(self)
                 
                    self.state = 299
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,24,self._ctx)

                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 300
                self.match(LuaParser.OP)
                self.state = 301
                self.exp(0)
                self.state = 302
                self.match(LuaParser.CP)
                self.state = 311
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,26,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 309
                        self._errHandler.sync(self)
                        token = self._input.LA(1)
                        if token in [47]:
                            self.state = 303
                            self.match(LuaParser.OB)
                            self.state = 304
                            self.exp(0)
                            self.state = 305
                            self.match(LuaParser.CB)
                            pass
                        elif token in [26]:
                            self.state = 307
                            self.match(LuaParser.DOT)
                            self.state = 308
                            self.match(LuaParser.NAME)
                            pass
                        else:
                            raise NoViableAltException(self)
                 
                    self.state = 313
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,26,self._ctx)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FunctioncallContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.NAME)
            else:
                return self.getToken(LuaParser.NAME, i)

        def OP(self):
            return self.getToken(LuaParser.OP, 0)

        def exp(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LuaParser.ExpContext)
            else:
                return self.getTypedRuleContext(LuaParser.ExpContext,i)


        def CP(self):
            return self.getToken(LuaParser.CP, 0)

        def args(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LuaParser.ArgsContext)
            else:
                return self.getTypedRuleContext(LuaParser.ArgsContext,i)


        def COL(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.COL)
            else:
                return self.getToken(LuaParser.COL, i)

        def OB(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.OB)
            else:
                return self.getToken(LuaParser.OB, i)

        def CB(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.CB)
            else:
                return self.getToken(LuaParser.CB, i)

        def DOT(self, i:int=None):
            if i is None:
                return self.getTokens(LuaParser.DOT)
            else:
                return self.getToken(LuaParser.DOT, i)

        def getRuleIndex(self):
            return LuaParser.RULE_functioncall

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFunctioncall" ):
                return visitor.visitFunctioncall(self)
            else:
                return visitor.visitChildren(self)




    def functioncall(self):

        localctx = LuaParser.FunctioncallContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_functioncall)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 321
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [56]:
                self.state = 316
                self.match(LuaParser.NAME)
                pass
            elif token in [30]:
                self.state = 317
                self.match(LuaParser.OP)
                self.state = 318
                self.exp(0)
                self.state = 319
                self.match(LuaParser.CP)
                pass
            else:
                raise NoViableAltException(self)

            self.state = 331
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==26 or _la==47:
                self.state = 329
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [47]:
                    self.state = 323
                    self.match(LuaParser.OB)
                    self.state = 324
                    self.exp(0)
                    self.state = 325
                    self.match(LuaParser.CB)
                    pass
                elif token in [26]:
                    self.state = 327
                    self.match(LuaParser.DOT)
                    self.state = 328
                    self.match(LuaParser.NAME)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 333
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 338
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [30, 45, 57, 58, 59]:
                self.state = 334
                self.args()
                pass
            elif token in [38]:
                self.state = 335
                self.match(LuaParser.COL)
                self.state = 336
                self.match(LuaParser.NAME)
                self.state = 337
                self.args()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 359
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,35,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 348
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    while _la==26 or _la==47:
                        self.state = 346
                        self._errHandler.sync(self)
                        token = self._input.LA(1)
                        if token in [47]:
                            self.state = 340
                            self.match(LuaParser.OB)
                            self.state = 341
                            self.exp(0)
                            self.state = 342
                            self.match(LuaParser.CB)
                            pass
                        elif token in [26]:
                            self.state = 344
                            self.match(LuaParser.DOT)
                            self.state = 345
                            self.match(LuaParser.NAME)
                            pass
                        else:
                            raise NoViableAltException(self)

                        self.state = 350
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)

                    self.state = 355
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [30, 45, 57, 58, 59]:
                        self.state = 351
                        self.args()
                        pass
                    elif token in [38]:
                        self.state = 352
                        self.match(LuaParser.COL)
                        self.state = 353
                        self.match(LuaParser.NAME)
                        self.state = 354
                        self.args()
                        pass
                    else:
                        raise NoViableAltException(self)
             
                self.state = 361
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,35,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArgsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OP(self):
            return self.getToken(LuaParser.OP, 0)

        def CP(self):
            return self.getToken(LuaParser.CP, 0)

        def explist(self):
            return self.getTypedRuleContext(LuaParser.ExplistContext,0)


        def tableconstructor(self):
            return self.getTypedRuleContext(LuaParser.TableconstructorContext,0)


        def string(self):
            return self.getTypedRuleContext(LuaParser.StringContext,0)


        def getRuleIndex(self):
            return LuaParser.RULE_args

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArgs" ):
                return visitor.visitArgs(self)
            else:
                return visitor.visitChildren(self)




    def args(self):

        localctx = LuaParser.ArgsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_args)
        try:
            self.state = 369
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [30]:
                self.enterOuterAlt(localctx, 1)
                self.state = 362
                self.match(LuaParser.OP)
                self.state = 364
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,36,self._ctx)
                if la_ == 1:
                    self.state = 363
                    self.explist()


                self.state = 366
                self.match(LuaParser.CP)
                pass
            elif token in [45]:
                self.enterOuterAlt(localctx, 2)
                self.state = 367
                self.tableconstructor()
                pass
            elif token in [57, 58, 59]:
                self.enterOuterAlt(localctx, 3)
                self.state = 368
                self.string()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FunctiondefContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FUNCTION(self):
            return self.getToken(LuaParser.FUNCTION, 0)

        def funcbody(self):
            return self.getTypedRuleContext(LuaParser.FuncbodyContext,0)


        def getRuleIndex(self):
            return LuaParser.RULE_functiondef

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFunctiondef" ):
                return visitor.visitFunctiondef(self)
            else:
                return visitor.visitChildren(self)




    def functiondef(self):

        localctx = LuaParser.FunctiondefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_functiondef)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 371
            self.match(LuaParser.FUNCTION)
            self.state = 372
            self.funcbody()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FuncbodyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OP(self):
            return self.getToken(LuaParser.OP, 0)

        def parlist(self):
            return self.getTypedRuleContext(LuaParser.ParlistContext,0)


        def CP(self):
            return self.getToken(LuaParser.CP, 0)

        def block(self):
            return self.getTypedRuleContext(LuaParser.BlockContext,0)


        def END(self):
            return self.getToken(LuaParser.END, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_funcbody

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFuncbody" ):
                return visitor.visitFuncbody(self)
            else:
                return visitor.visitChildren(self)




    def funcbody(self):

        localctx = LuaParser.FuncbodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_funcbody)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 374
            self.match(LuaParser.OP)
            self.state = 375
            self.parlist()
            self.state = 376
            self.match(LuaParser.CP)
            self.state = 377
            self.block()
            self.state = 378
            self.match(LuaParser.END)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParlistContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def namelist(self):
            return self.getTypedRuleContext(LuaParser.NamelistContext,0)


        def COMMA(self):
            return self.getToken(LuaParser.COMMA, 0)

        def DDD(self):
            return self.getToken(LuaParser.DDD, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_parlist

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParlist" ):
                return visitor.visitParlist(self)
            else:
                return visitor.visitChildren(self)




    def parlist(self):

        localctx = LuaParser.ParlistContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_parlist)
        self._la = 0 # Token type
        try:
            self.state = 387
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [56]:
                self.enterOuterAlt(localctx, 1)
                self.state = 380
                self.namelist()
                self.state = 383
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==15:
                    self.state = 381
                    self.match(LuaParser.COMMA)
                    self.state = 382
                    self.match(LuaParser.DDD)


                pass
            elif token in [54]:
                self.enterOuterAlt(localctx, 2)
                self.state = 385
                self.match(LuaParser.DDD)
                pass
            elif token in [31]:
                self.enterOuterAlt(localctx, 3)

                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TableconstructorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OCU(self):
            return self.getToken(LuaParser.OCU, 0)

        def CCU(self):
            return self.getToken(LuaParser.CCU, 0)

        def fieldlist(self):
            return self.getTypedRuleContext(LuaParser.FieldlistContext,0)


        def getRuleIndex(self):
            return LuaParser.RULE_tableconstructor

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTableconstructor" ):
                return visitor.visitTableconstructor(self)
            else:
                return visitor.visitChildren(self)




    def tableconstructor(self):

        localctx = LuaParser.TableconstructorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_tableconstructor)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 389
            self.match(LuaParser.OCU)
            self.state = 391
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,40,self._ctx)
            if la_ == 1:
                self.state = 390
                self.fieldlist()


            self.state = 393
            self.match(LuaParser.CCU)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FieldlistContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def field(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LuaParser.FieldContext)
            else:
                return self.getTypedRuleContext(LuaParser.FieldContext,i)


        def fieldsep(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LuaParser.FieldsepContext)
            else:
                return self.getTypedRuleContext(LuaParser.FieldsepContext,i)


        def getRuleIndex(self):
            return LuaParser.RULE_fieldlist

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFieldlist" ):
                return visitor.visitFieldlist(self)
            else:
                return visitor.visitChildren(self)




    def fieldlist(self):

        localctx = LuaParser.FieldlistContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_fieldlist)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 395
            self.field()
            self.state = 401
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,41,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 396
                    self.fieldsep()
                    self.state = 397
                    self.field() 
                self.state = 403
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,41,self._ctx)

            self.state = 405
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1 or _la==15:
                self.state = 404
                self.fieldsep()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FieldContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OB(self):
            return self.getToken(LuaParser.OB, 0)

        def exp(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LuaParser.ExpContext)
            else:
                return self.getTypedRuleContext(LuaParser.ExpContext,i)


        def CB(self):
            return self.getToken(LuaParser.CB, 0)

        def EQ(self):
            return self.getToken(LuaParser.EQ, 0)

        def NAME(self):
            return self.getToken(LuaParser.NAME, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_field

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitField" ):
                return visitor.visitField(self)
            else:
                return visitor.visitChildren(self)




    def field(self):

        localctx = LuaParser.FieldContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_field)
        try:
            self.state = 417
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,43,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 407
                self.match(LuaParser.OB)
                self.state = 408
                self.exp(0)
                self.state = 409
                self.match(LuaParser.CB)
                self.state = 410
                self.match(LuaParser.EQ)
                self.state = 411
                self.exp(0)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 413
                self.match(LuaParser.NAME)
                self.state = 414
                self.match(LuaParser.EQ)
                self.state = 415
                self.exp(0)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 416
                self.exp(0)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FieldsepContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COMMA(self):
            return self.getToken(LuaParser.COMMA, 0)

        def SEMI(self):
            return self.getToken(LuaParser.SEMI, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_fieldsep

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFieldsep" ):
                return visitor.visitFieldsep(self)
            else:
                return visitor.visitChildren(self)




    def fieldsep(self):

        localctx = LuaParser.FieldsepContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_fieldsep)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 419
            _la = self._input.LA(1)
            if not(_la==1 or _la==15):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NumberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(LuaParser.INT, 0)

        def HEX(self):
            return self.getToken(LuaParser.HEX, 0)

        def FLOAT(self):
            return self.getToken(LuaParser.FLOAT, 0)

        def HEX_FLOAT(self):
            return self.getToken(LuaParser.HEX_FLOAT, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_number

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNumber" ):
                return visitor.visitNumber(self)
            else:
                return visitor.visitChildren(self)




    def number(self):

        localctx = LuaParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 421
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & -1152921504606846976) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StringContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NORMALSTRING(self):
            return self.getToken(LuaParser.NORMALSTRING, 0)

        def CHARSTRING(self):
            return self.getToken(LuaParser.CHARSTRING, 0)

        def LONGSTRING(self):
            return self.getToken(LuaParser.LONGSTRING, 0)

        def getRuleIndex(self):
            return LuaParser.RULE_string

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitString" ):
                return visitor.visitString(self)
            else:
                return visitor.visitChildren(self)




    def string(self):

        localctx = LuaParser.StringContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_string)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 423
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1008806316530991104) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[12] = self.exp_sempred
        self._predicates[14] = self.prefixexp_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def exp_sempred(self, localctx:ExpContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 12)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 10)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 9)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 8)
         

            if predIndex == 4:
                return self.precpred(self._ctx, 7)
         

            if predIndex == 5:
                return self.precpred(self._ctx, 6)
         

            if predIndex == 6:
                return self.precpred(self._ctx, 5)
         

            if predIndex == 7:
                return self.precpred(self._ctx, 4)
         

            if predIndex == 8:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 9:
                return self.precpred(self._ctx, 2)
         

            if predIndex == 10:
                return self.precpred(self._ctx, 1)
         

    def prefixexp_sempred(self, localctx:PrefixexpContext, predIndex:int):
            if predIndex == 11:
                return  self.IsFunctionCall() 
         




