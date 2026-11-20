-- ordenamientos, primos, fibonacci, gcd, hanoi, n-reinas
local function bubble(t) local n=#t for i=1,n do for j=1,n-i do if t[j]>t[j+1] then t[j],t[j+1]=t[j+1],t[j] end end end return t end
local function quick(t) if #t<2 then return t end local p=t[1] local l,r={}, {} for i=2,#t do if t[i]<p then l[#l+1]=t[i] else r[#r+1]=t[i] end end
  local res=quick(l) res[#res+1]=p for _,v in ipairs(quick(r)) do res[#res+1]=v end return res end
local function merge(a,b) local r,i,j={},1,1 while i<=#a and j<=#b do if a[i]<=b[j] then r[#r+1]=a[i] i=i+1 else r[#r+1]=b[j] j=j+1 end end
  while i<=#a do r[#r+1]=a[i] i=i+1 end while j<=#b do r[#r+1]=b[j] j=j+1 end return r end
local function msort(t) if #t<2 then return t end local m=#t//2 local a,b={}, {} for i=1,m do a[i]=t[i] end for i=m+1,#t do b[#b+1]=t[i] end return merge(msort(a),msort(b)) end
local data={5,3,9,1,5,8,2,7,0,-4,12,6}
print(table.concat(bubble({table.unpack(data)}),","))
print(table.concat(quick(data),","))
print(table.concat(msort(data),","))
local function sieve(n) local is={} for i=2,n do is[i]=true end for i=2,math.floor(math.sqrt(n)) do if is[i] then for j=i*i,n,i do is[j]=false end end end
  local r={} for i=2,n do if is[i] then r[#r+1]=i end end return r end
print(table.concat(sieve(100)," "))
local function fib(n) local a,b=0,1 for _=1,n do a,b=b,a+b end return a end
print(fib(10),fib(50),fib(90))
local function gcd(a,b) while b~=0 do a,b=b,a%b end return a end
print(gcd(48,18),gcd(17,5),gcd(0,9))
local moves=0
local function hanoi(n,a,b,c) if n==0 then return end hanoi(n-1,a,c,b) moves=moves+1 hanoi(n-1,c,b,a) end
hanoi(10,"A","B","C") print(moves)
local function queens(n) local cols,count={}, 0
  local function ok(r,c) for i=1,r-1 do if cols[i]==c or math.abs(cols[i]-c)==r-i then return false end end return true end
  local function place(r) if r>n then count=count+1 return end for c=1,n do if ok(r,c) then cols[r]=c place(r+1) end end end
  place(1) return count end
print(queens(6),queens(7))
local function fact(n) if n<=1 then return 1 end return n*fact(n-1) end
print(fact(10),fact(20),fact(21),fact(25))
print(2^10, 2^0.5, 10//3, 10%3, -10//3, -10%3, 10.5//3, 10.5%3)
local function binsearch(t,x) local lo,hi=1,#t while lo<=hi do local m=(lo+hi)//2 if t[m]==x then return m elseif t[m]<x then lo=m+1 else hi=m-1 end end return nil end
print(binsearch(msort(data),8),binsearch(msort(data),100))
local memo={} local function mfib(n) if n<2 then return n end if memo[n] then return memo[n] end local v=mfib(n-1)+mfib(n-2) memo[n]=v return v end
print(mfib(80))
local function collatz(n) local s=0 while n~=1 do if n%2==0 then n=n//2 else n=3*n+1 end s=s+1 end return s end
print(collatz(27),collatz(97))
