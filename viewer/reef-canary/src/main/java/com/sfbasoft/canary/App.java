package com.sfbasoft.canary;

import org.apache.reef.client.REEF;
import org.apache.reef.client.*;
import org.apache.reef.tang.*;
import org.apache.reef.tang.exceptions.*;
import org.apache.reef.driver.context.*;
import org.apache.reef.driver.evaluator.*;
import org.apache.reef.driver.task.*;
import org.apache.reef.wake.*;
import org.apache.reef.wake.time.event.*;

import org.apache.reef.runtime.yarn.driver.*;
import org.apache.reef.runtime.yarn.client.*;
import org.apache.reef.util.*;

import javax.inject.Inject;
/**
 * Canary
 */
public class App 
{
    private static final int MAX_NUMBER_OF_EVALUATORS = 3;
    private static final int JOB_TIMEOUT = 10000;

    public static void main(final String[] args) {
        final Tang tang = Tang.Factory.getTang();
        try {
            final Configuration runtimeConf = YarnClientConfiguration.CONF.build();

            final Configuration driverConf = DriverConfiguration.CONF
                    .setMultiple(DriverConfiguration.GLOBAL_LIBRARIES, EnvironmentUtils.getAllClasspathJars())
                    .set(DriverConfiguration.DRIVER_IDENTIFIER, "Canary")
                    .set(DriverConfiguration.ON_DRIVER_STARTED, StartHandler.class)
                    .set(DriverConfiguration.ON_EVALUATOR_ALLOCATED, EvaluatorAllocatedHandler.class)
                    .set(DriverConfiguration.ON_CONTEXT_ACTIVE, ActiveContextHandler.class)
                    .set(DriverConfiguration.ON_TASK_COMPLETED, CompletedTaskHandler.class)
                    .build();

            final LauncherStatus status = DriverLauncher.getLauncher(runtimeConf).run(driverConf, JOB_TIMEOUT);
        } catch (InjectionException e) {
            System.out.println("FAIL TO LAUNCH CANARY APP");
            e.printStackTrace();
        }
    }

    private final EvaluatorRequestor requestor;

    @Inject
    private App(final EvaluatorRequestor requestor) {
        this.requestor = requestor;
    }

    private synchronized void requestEvaluator(final int numToRequest) {
        if (numToRequest <= 0) {
            throw new IllegalArgumentException("The number of evaluator request should be a positive integer");
        }
    }

    public final class StartHandler implements EventHandler<StartTime> {
        @Override
        public void onNext(final StartTime startTime) {
            synchronized (App.this) {
                requestor.submit(EvaluatorRequest.newBuilder()
                        .setMemory(32)
                        .setNumber(MAX_NUMBER_OF_EVALUATORS)
                        .build());
            }
        }
    }

    public final class EvaluatorAllocatedHandler implements EventHandler<AllocatedEvaluator> {
        @Override
        public void onNext(final AllocatedEvaluator evaluator) {
            evaluator.submitContext(ContextConfiguration.CONF
                    .set(ContextConfiguration.IDENTIFIER, "CanaryContext")
                    .build());
        }
    }

    public final class ActiveContextHandler implements EventHandler<ActiveContext> {
        @Override
        public void onNext(final ActiveContext context) {
            synchronized (App.this) {
                context.close();
                //scheduler.submitTask(context);
            }
        }
    }

    public final class CompletedTaskHandler implements EventHandler<CompletedTask> {
        @Override
        public void onNext(final CompletedTask task) {
            final int taskId = Integer.parseInt(task.getId());

            synchronized (App.this) {
                final ActiveContext context = task.getActiveContext();
            }
        }
    }
}
