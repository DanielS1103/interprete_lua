local t={10,20,30}
table.insert(t,40) table.insert(t,1,5) table.insert(t,3,15)
print(table.concat(t,","),#t)
print(table.remove(t),table.remove(t,1),table.remove(t,2),table.concat(t,","))
print(table.remove({}),table.remove({},0),#t)
print(table.concat({},","),table.concat({1},","),table.concat({1,2,3},", ",2,3),table.concat({1,2,3},"",3,2))
print(table.unpack({1,2,3})) print(table.unpack({1,2,3},2)) print(table.unpack({1,2,3},2,5)) print(table.unpack({},1,2))
local p=table.pack(1,nil,3,nil) print(p.n,p[1],p[2],p[3],p[4])
print(select("#",table.unpack({n=3},1,3)))
local m=table.move({1,2,3},1,3,2) print(table.concat(m,","))
local m2=table.move({1,2,3},1,3,1,{}) print(table.concat(m2,","))
local words={"banana","apple","Cherry","date"} table.sort(words) print(table.concat(words," "))
table.sort(words,function(a,b) return a:lower()<b:lower() end) print(table.concat(words," "))
local nums={5,2,8,1,9,3} table.sort(nums,function(a,b) return a>b end) print(table.concat(nums," "))
local recs={{n="a",v=3},{n="b",v=1},{n="c",v=2}} table.sort(recs,function(x,y) return x.v<y.v end)
for _,r in ipairs(recs) do io.write(r.n,r.v," ") end print()
print(pcall(table.sort,{3,"a",1}))
-- pairs / ipairs / next
local mixed={1,2,3,x=1,y=2}
local n=0 for k,v in pairs(mixed) do n=n+1 end print(n)
for i,v in ipairs({1,2,nil,4}) do io.write(i,":",v," ") end print()
local keys={} for k in pairs({a=1,b=2,c=3}) do keys[#keys+1]=k end table.sort(keys) print(table.concat(keys))
print(next({}),next({5}),type(next))
local tt={} for i=1,10 do tt[i]=i end for i=1,10 do if i%2==0 then tt[i]=nil end end
local c=0 for _ in pairs(tt) do c=c+1 end print(c)
-- modificar durante el recorrido (asignar nil a existente)
local d={a=1,b=2,c=3,d=4} for k in pairs(d) do d[k]=nil end print(next(d))
-- longitud
print(#{},#{1},#{1,2,3},#{n=1},#{1,2,nil,4}==4 or #{1,2,nil,4}==2)
local g={} g[1]=1 g[2]=2 g[4]=4 print(#g==2 or #g==4)
local h={} for i=1,100 do h[#h+1]=i end print(#h,h[100]) for i=1,50 do h[#h]=nil end print(#h)
-- llaves variadas
local k={} k[1]="int" k[1.5]="float" k["1"]="str" k[true]="bool" k[k]="self"
print(k[1],k[1.5],k["1"],k[true],k[k],k[1.0],k[2^0])
k[2^53]="big" print(k[2^53],k[9007199254740992])
print(pcall(function() k[nil]=1 end))
print(pcall(function() k[0/0]=1 end))
print(k[nil],k[0/0])
-- matrices
local function matmul(a,b) local r={} for i=1,#a do r[i]={} for j=1,#b[1] do local s=0 for l=1,#b do s=s+a[i][l]*b[l][j] end r[i][j]=s end end return r end
local r=matmul({{1,2},{3,4}},{{5,6},{7,8}}) print(r[1][1],r[1][2],r[2][1],r[2][2])
-- math
print(math.floor(-0.5),math.ceil(-0.5),math.floor(5),math.ceil(5.0001),math.abs(-0.0),math.abs(math.mininteger))
print(math.max(1,2.5,2),math.min(3,1,2),math.max(-1/0,1/0),pcall(math.max))
print(math.fmod(7,3),math.fmod(-7,3),math.fmod(7,-3),math.fmod(5.5,2),pcall(math.fmod,1,0))
print(math.sqrt(2),math.sin(0),math.cos(0),math.exp(0),math.log(1),math.log(8,2),math.log(100,10))
print(math.tointeger(3.0),math.tointeger(3.5),math.tointeger("8"),math.tointeger({}),math.type(1),math.type(1.0),math.type("1"))
print(math.huge,-math.huge,math.pi,math.maxinteger,math.mininteger,math.maxinteger+1==math.mininteger)
print(math.ult(1,-1),math.ult(-1,1),7//2,-7//2,7%-3,-7%-3,7.5%2,-7.5%2)
print(5//0.0,-5//0.0,0/0~=0/0,math.huge-math.huge~=0)
math.randomseed(42) local r1=math.random() print(r1>=0 and r1<1,math.random(10)<=10,math.random(5,6)>=5)
print(pcall(math.random,0),pcall(math.random,2,1))
print(8//3,8.0//3,2^2,7/2,3|4,3~5,~0,1<<4,256>>4,"5"+0,"0x10"+0,"1e1"+0)
-- tonumber
print(tonumber("10"),tonumber("  10  "),tonumber("10a"),tonumber("0x1F"),tonumber("1e3"),tonumber("-5"),tonumber("- 5"),tonumber(""),tonumber(nil),tonumber(true),tonumber({}))
print(tonumber("z",36),tonumber("ff",16),tonumber("FF",16),tonumber("8",8),tonumber("777",8),tonumber("1.5",10),tonumber("-ff",16))
print(tonumber("inf"),tonumber("nan"),tonumber("0x"),tonumber("1_000"),tonumber("١"),tonumber(".5"),tonumber("5."),tonumber("0x.8"))
print(tostring(3)==("3"),tostring(3.0),tostring(-0.0),tostring(1e300*1e10),tostring(2^63),tostring(10//1),tostring(10/1))
-- select
print(select("#"),select("#",nil),select("#",nil,nil),select(2,"a","b","c"),select(-2,"a","b","c"))
print(pcall(select,0),pcall(select,-5,1))
-- os/io
io.write("a","b",1,2.5,"\n") print(io.write("") == io.stdout)
print(type(os.time()),type(os.clock()),type(os.date()),os.date("%Y-%m-%d",0)=="1970-01-01" or true)
print(os.time({year=2020,month=1,day=1,hour=12})>0,os.getenv("____NOPE"))
