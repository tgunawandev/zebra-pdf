#!/bin/bash
echo "🔍 Getting default API token from container logs..."
docker logs zebra-print-control 2>&1 | grep "🔑 Generated default API token:" | tail -1 | sed 's/.*🔑 Generated default API token: //'