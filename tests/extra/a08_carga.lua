-- pruebas de carga moderada
local t0=os.clock()
local N=30000
local t={} for i=1,N do t[i]=(i*7919)%10007 end
table.sort(t) print(t[1],t[N//2],t[N])
local sum=0 for i=1,200000 do sum=sum+(i%13)*(i%7) end print(sum)
local parts={} for i=1,5000 do parts[#parts+1]=string.format("%04d",i) end local s=table.concat(parts) print(#s,s:sub(1,12),s:sub(-4))
local cnt=0 for w in s:gmatch("%d%d%d%d") do cnt=cnt+1 end print(cnt)
local m={} for i=1,20000 do m["k"..i]=i end local c=0 for k,v in pairs(m) do c=c+v end print(c)
local function fib(n) if n<2 then return n end return fib(n-1)+fib(n-2) end print(fib(22))
local q={} for i=1,10000 do table.insert(q,i) end local r=0 while #q>0 do r=r+table.remove(q) end print(r)
local str="" for i=1,2000 do str=str..i end print(#str)
local grid={} for i=1,100 do grid[i]={} for j=1,100 do grid[i][j]=i*j end end local tot=0 for i=1,100 do for j=1,100 do tot=tot+grid[i][j] end end print(tot)
local primes=0 for n=2,5000 do local isp=true for d=2,math.floor(math.sqrt(n)) do if n%d==0 then isp=false break end end if isp then primes=primes+1 end end print(primes)
local depth=0 local function dive(n) if n==0 then return 0 end return 1+dive(n-1) end print(dive(3000))
local co=coroutine.wrap(function() for i=1,20000 do coroutine.yield(i) end end) local cs=0 for i=1,20000 do cs=cs+co() end print(cs)
io.stderr:write(string.format("tiempo %.2f\n",os.clock()-t0))
