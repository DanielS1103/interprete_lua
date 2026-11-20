-- goto, bucles, scoping
for i=1,3 do for j=1,3 do if j==2 then goto cont end io.write(i,j," ") ::cont:: end end print()
do local i=1 ::top:: if i<=3 then io.write(i," ") i=i+1 goto top end print() end
for i=10,1,-3 do io.write(i," ") end print()
for i=1,0 do print("never") end
for i=1.5,3 do io.write(i," ") end print()
for i=1,3 do local i=i*2 io.write(i," ") end print()
for i=math.maxinteger-2,math.maxinteger do io.write(i," ") end print()
local n=0 while true do n=n+1 if n>5 then break end end print(n)
local r=0 repeat local x=r r=r+1 until x>=3 print(r)
local function f() for i=1,10 do if i==4 then return i end end end print(f())
-- varargs
local function va(...) return select("#",...),... end
print(va()) print(va(nil)) print(va(1,nil,nil)) print((va(1,2,3)))
local function sum(...) local s=0 for _,v in ipairs({...}) do s=s+v end return s end print(sum(1,2,3,4),sum())
local function tail(...) return ... end print(tail(1,2,3),tail(4,5))
print(table.pack(tail()).n,table.pack(tail(nil,nil)).n)
local function opt(a,b,c) return a,b,c end print(opt(1),opt(1,2,3,4))
print((opt(1,2,3)))
local t={opt(1,2),opt(3,4)} print(#t)
local t2={opt(1,2),(opt(3,4))} print(#t2)
-- closures
local function counter() local c=0 return function() c=c+1 return c end,function() return c end end
local inc,get=counter() inc() inc() print(get())
local fs={} for i=1,3 do fs[#fs+1]=function() i=i+10 return i end end print(fs[1](),fs[1](),fs[2]())
local x=1 local function addx(y) return x+y end x=10 print(addx(1))
local function outer() local a=1 local function mid() local function inner() a=a+1 return a end return inner end return mid() end
local inn=outer() print(inn(),inn())
-- recursion mutua
local isodd local function iseven(n) if n==0 then return true end return isodd(n-1) end
function isodd(n) if n==0 then return false end return iseven(n-1) end print(iseven(100),isodd(7))
-- shadowing
local v=1 do local v=v+1 do local v=v+1 print(v) end print(v) end print(v)
-- definicion de metodos anidados
local M={a={b={}}} function M.a.b.f(x) return x*2 end function M.a.b:g(x) return self==M.a.b,x end
print(M.a.b.f(4),M.a.b:g(5))
-- globales
gx=5 print(gx,_G.gx,_G["gx"],rawget(_G,"gx")) _G.gy=7 print(gy) gx=nil print(gx)
-- corrutinas
local function gen(n) return coroutine.wrap(function() for i=1,n do coroutine.yield(i,i*i) end end) end
for a,b in gen(4) do io.write(a,":",b," ") end print()
local co=coroutine.create(function(a,b)
  print("start",a,b)
  local c=coroutine.yield(a+b)
  print("got",c)
  local d,e=coroutine.yield(c*2)
  print("got2",d,e)
  return "fin",99
end)
print(coroutine.resume(co,1,2)) print(coroutine.status(co))
print(coroutine.resume(co,10)) print(coroutine.resume(co,"x","y")) print(coroutine.status(co))
print(coroutine.resume(co)) print(coroutine.resume(coroutine.create(function() return end)))
print(pcall(coroutine.resume,nil))
print(select("#",coroutine.resume(coroutine.create(function() return nil,nil end))))
-- yield desde funciones anidadas y pcall
local co2=coroutine.create(function()
  local function deep(n) if n==0 then coroutine.yield("bottom") else deep(n-1) end return n end
  local ok,v=pcall(deep,5) coroutine.yield(ok,v)
  local ok2,err=pcall(function() coroutine.yield("in pcall") error("oops",0) end)
  return ok2,err
end)
for i=1,4 do print(coroutine.resume(co2)) end
-- productor/consumidor
local function producer() return coroutine.create(function() for _,v in ipairs{"a","b","c"} do coroutine.yield(v) end end) end
local function consumer(p) local out={} while true do local ok,v=coroutine.resume(p) if not v then break end out[#out+1]=v end return table.concat(out) end
print(consumer(producer()))
-- estado y running
local co3 co3=coroutine.create(function() print(coroutine.status(co3),coroutine.isyieldable()) local _,main=coroutine.running() print(main) end)
coroutine.resume(co3) print(coroutine.status(co3),coroutine.isyieldable(),select(2,coroutine.running()))
print(coroutine.close(coroutine.create(function() end)))
local w=coroutine.wrap(function() return 1 end) w() print(pcall(w))
print(pcall(coroutine.yield,1))
-- muchos coroutines
local list={} for i=1,200 do list[i]=coroutine.wrap(function() local s=0 while true do s=s+i coroutine.yield(s) end end) end
local tot=0 for r=1,3 do for i=1,200 do tot=tot+list[i]() end end print(tot)
-- fibonacci con coroutines
local fibgen=coroutine.wrap(function() local a,b=0,1 while true do coroutine.yield(a) a,b=b,a+b end end)
local fl={} for i=1,15 do fl[i]=fibgen() end print(table.concat(fl," "))
-- load
print(load("return 1+1")(),load("syntax error here"))
print(load("local a,b=... return b,a")(1,2))
local env={print=print,x=3} print(load("x=x+1 return x",nil,"t",env)(),env.x,x)
print(pcall(load("error('in load')")))
local chunks={"return ","'pieces'"} local ci=0 print(load(function() ci=ci+1 return chunks[ci] end)())
-- integer overflow y conversiones
print(math.maxinteger+1==math.mininteger,math.mininteger-1==math.maxinteger,math.maxinteger*2,-math.mininteger)
print(1e308*10,-1e308*10,2^1024,math.tointeger(2^63),string.format("%d",2^31))
print(0x7fffffffffffffff,0xffffffffffffffff,0x10000000000000000,9223372036854775807,9223372036854775808)
print(1//1,1.0//1,2^2,4//2,4/2,3%math.huge,-3%math.huge,3%-math.huge)
print(100000000000000,1e14,123456.789e3,0.1+0.2==0.3,0.1+0.2,1/3)
print(255==0xff,1e2==100,"1"==1,0==-0,1/0==math.huge)
