"use strict";(globalThis.webpackChunk_coral_xyz_app_extension=globalThis.webpackChunk_coral_xyz_app_extension||[]).push([[981],{17981:(e,a,t)=>{t.r(a),t.d(a,{default:()=>d});var r=t(81563),n=t(98091),o=t(39811),s=t(12931),i=t(70376),c=t(32692),l=t(91693),u=t(2784);function d(){const{publicKey:e}=(0,r.rTu)(),a=(0,i.HJ)(),t=(0,n.Xi)(e),{data:d,isError:p,isLoading:h}=t,g=p?"Error fetching accounts":h?void 0:d&&d.length>0?`${d.length} account${d.length>1?"s":""}`:"Stake some SOL",k=d&&d?.length>0?`${(0,o.bv)(d.reduce(((e,a)=>e+a.lamports),0),{appendTicker:!0})}`:"",v=(0,n.lC)(e),b=v.data?.reduce(((e,[a,t])=>e+(t?.amount??0)),0),_=void 0!==b?b>0?`+${(0,o.bv)(b,{appendTicker:!0})}`:"":void 0;return u.createElement(s.g,{subtitle:g,total:k,totalRewards:_,onPress:p?void 0:()=>{a.push(l.Z.StakeNavigator,{screen:c.Z.ListStakesScreen,params:void 0})}})}}}]);