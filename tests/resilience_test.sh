#!/bin/bash
NAMESPACE="hipstershop"
DEPLOYMENT="frontend"

echo "Simulating pod failure..."
POD=$(kubectl get pods -n $NAMESPACE -l app=$DEPLOYMENT -o name | head -n 1)
kubectl delete $POD -n $NAMESPACE

echo "Waiting for pod recovery..."
START=$(date +%s)
while true; do
  READY=$(kubectl get deploy $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
  if [ "$READY" == "1" ]; then
    END=$(date +%s)
    break
  fi
  sleep 5
done
echo "Recovery time: $((END - START)) seconds"
