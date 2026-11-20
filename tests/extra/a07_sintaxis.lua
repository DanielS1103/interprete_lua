-- sintaxis y precedencia
print(2+3*4^2/2, (2+3)*4, 2^3^2, -2^2, not nil==true, not (nil==true), 1 .. 2 .. 3)
print(1+2 .. "x", "a".."b"=="ab", 1<2==true, "x"=="x" and 1 or 2, nil and 1 or 2, false or nil, nil or false)
print(7&3|8, 7&(3|8), 1|2~3, 5~3&1, 1<<2+1, (1<<2)+1, 6&3==2, 0xF0>>4&0x3, ~5&0xFF, -3>>1==(-3)>>1)
print(1+1==2 and 2+2==4, 3>2 and 2>1, 1<2 and "a" or "b", #"abc"+1, -#"abc", not not nil)
print(10-2-3, 2^-1, 100/10/5, 7//2//2, 2*3%4, 1+2<4, "a".."b".."c"=="abc", -(-3), - -3)
print(8%3.5, 2^53+1, 1e2, 0x.8, 0xA.8p1, 3e-2, 0e0, 0xaBc)
-- literales de cadena
print('single','dbl "q"',"it's",'esc \'q\'',"tab\there","nl\\n",'\65\066\x43\u{44}',"\z
       joined", #"\n\r\t\a\b\f\v\\\"\'")
print([[long
string]],[==[with ]] inside]==],[[
skip first newline]],#[[

]])
--[[ comentario
largo ]] print("tras comentario") --[==[ otro
]==] print("tras otro")
-- comment at end without newline follows
print(#"áé", "ñ", ("ñ"):byte(1,-1))
-- llamadas encadenadas y azucar
local obj={name="o"} function obj:set(n) self.name=n return self end function obj:get() return self.name end
print(obj:set("a"):set("b"):get())
print(("x"):rep(3), #("abc"), ("%d"):format(5), type"x", type{}, tostring{}~=nil)
local function f(t) return t[1] or t.k end print(f{9}, f{k="kk"}, f"str" == nil)
print((function(...) return select("#",...) end)(1,2,3))
print(#{...}, select("#",...))
local t={[1]="a";"b",c=3;[2+1]="d",} print(t[1],t[3],t.c,#t)
local t3={f=function() return 1 end,["g h"]=2,[10]=3,[-1]=4,[1.5]=5} print(t3.f(),t3["g h"],t3[10],t3[-1],t3[1.5])
local nested={{1,2},{3,{4,5}}} print(nested[2][2][1],#nested[2])
;;; local z=1; ; print(z);
local a,b,c=(function() return 1,2,3 end)() print(a,b,c)
local d,e=((function() return 1,2 end)()) print(d,e)
local q = {} q.x, q.y = 1 print(q.x, q.y)
local i=1 local arr={} i,arr[i]=i+1,"v" print(i,arr[1],arr[2])
local x1,x2,x3 = 1 print(x1,x2,x3)
local u1,u2 = 1,2,3 print(u1,u2)
do local a <const> = 5 local b <close> = nil print(a,b) end
-- while con condicion compleja, break en anidado
local cnt=0 for i=1,10 do for j=1,10 do if j>i then break end cnt=cnt+1 end end print(cnt)
local k=0 while k<100 do k=k+1 if k%7==0 and k%5==0 then break end end print(k)
-- if encadenado
local function cls(n) if n<0 then return "neg" elseif n==0 then return "zero" elseif n<10 then return "small" else return "big" end end
print(cls(-1),cls(0),cls(5),cls(50))
-- ejecucion de strings numericos con operadores
print("10"/2, "3"^2, "7"//2, "7"%4, -"2", "0x10"*1, 10 .. "" == "10")
print(math.type("10"+0), math.type("10.0"+0), math.type("1e1"+0))
-- comparaciones mixtas
print(1==1.0, 1<1.5, 2^53==2^53+1, math.maxinteger<math.huge, math.mininteger>-math.huge, 1<2.0)
print(math.maxinteger+0.0==math.maxinteger, math.maxinteger+0.0, 2^63==math.maxinteger+1.0)
print("a"<"b", "a"<="a", "b">"a", "abc"<"abd", ""<"a")
-- negativos y cero
print(0.0==-0.0, 1/0.0, 1/-0.0, 0.0, -0.0, 3%-2, -3%2, 3.5%-2, -3.5%2, 5//-2, -5//2, 5.0//-2)
