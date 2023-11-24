for f in crab_muRPCTnPFlatTableProducer_cfg*; do
  echo "--------------------------------------------"
  echo "Kill -> $f"
  crab kill $f
  rm -rf $f
done
