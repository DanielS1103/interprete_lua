local Animal={} Animal.__index=Animal
function Animal.new(name,sound) local self=setmetatable({},Animal) self.name=name self.sound=sound return self end
function Animal:speak() return self.name.." says "..self.sound end
local Dog=setmetatable({},{__index=Animal}) Dog.__index=Dog
function Dog.new(name) local self=Animal.new(name,"woof") return setmetatable(self,Dog) end
function Dog:fetch() return self.name.." fetches!" end
local d=Dog.new("Rex") print(d:speak(),d:fetch(),getmetatable(d)==Dog)
-- Vector con operadores
local V={} V.__index=V
local function vec(x,y) return setmetatable({x=x,y=y},V) end
V.__add=function(a,b) return vec(a.x+b.x,a.y+b.y) end
V.__sub=function(a,b) return vec(a.x-b.x,a.y-b.y) end
V.__mul=function(a,b) if type(a)=="number" then return vec(a*b.x,a*b.y) elseif type(b)=="number" then return vec(a.x*b,a.y*b) else return a.x*b.x+a.y*b.y end end
V.__eq=function(a,b) return a.x==b.x and a.y==b.y end
V.__lt=function(a,b) return a.x<b.x end V.__le=function(a,b) return a.x<=b.x end
V.__tostring=function(v) return "("..v.x..","..v.y..")" end
V.__len=function(v) return 2 end V.__unm=function(v) return vec(-v.x,-v.y) end
V.__concat=function(a,b) return tostring(a)..tostring(b) end
V.__call=function(v,k) return v[k] end
V.__idiv=function(a,b) return vec(a.x//b,a.y//b) end V.__mod=function(a,b) return vec(a.x%b,a.y%b) end
local a,b=vec(1,2),vec(3,4)
print(tostring(a+b),tostring(a-b),a*b,tostring(2*a),tostring(a*3),a==vec(1,2),a~=b,a<b,a<=b,a>b,a>=b)
print(#a,tostring(-a),a..b,a.."x","x"..a,a("x"),tostring(vec(7,9)//2),tostring(vec(7,9)%4))
-- pila
local Stack={} Stack.__index=Stack
function Stack.new() return setmetatable({n=0},Stack) end
function Stack:push(v) self.n=self.n+1 self[self.n]=v end
function Stack:pop() local v=self[self.n] self[self.n]=nil self.n=self.n-1 return v end
local s=Stack.new() for i=1,5 do s:push(i*i) end print(s:pop(),s:pop(),s.n)
-- proxy con __index/__newindex/__pairs
local log={}
local function proxy(t) return setmetatable({},{__index=function(_,k) log[#log+1]="get "..tostring(k) return t[k] end,__newindex=function(_,k,v) log[#log+1]="set "..tostring(k) t[k]=v end,__pairs=function() return next,t,nil end}) end
local p=proxy({a=1}) p.b=2 local _=p.a+p.b print(table.concat(log,";"))
local cnt=0 for k,v in pairs(p) do cnt=cnt+v end print(cnt)
-- valores por defecto
local def=setmetatable({},{__index=function() return 0 end}) def.x=def.x+1 def.x=def.x+1 print(def.x,def.y)
-- herencia multiple simple
local function createClass(...) local parents={...} local c={} setmetatable(c,{__index=function(t,k) for _,p in ipairs(parents) do local v=p[k] if v then return v end end end}) c.__index=c return c end
local A={foo=function() return "A.foo" end} local B={bar=function() return "B.bar" end}
local C=createClass(A,B) local o=setmetatable({},C) print(o.foo(),o.bar())
-- clausura como objeto
local function account(bal) return {deposit=function(n) bal=bal+n return bal end,balance=function() return bal end} end
local acc=account(100) acc.deposit(50) print(acc.balance())
print(rawequal(a,vec(1,2)),rawlen({1,2,3}),rawget(a,"x"))
